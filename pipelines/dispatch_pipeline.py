from typing import List, Dict, Any, Optional
from models.map_graph import CityGridMap
from models.vehicle import Vehicle
from models.incident import Incident, IncidentStatus
from perception.nlp_engine import NLPEngine
from perception.vision_engine import VisionEngine
from core.csp_solver import CSPSolver
from core.pathfinding import AStarPlanner
from core.logic_rules import LogicEngine
from core.probabilistic_engine import ProbabilisticEngine
from core.rl_rebalancer import RLRebalancer
from analytics.demand_forecaster import DemandForecaster
from pipelines.event_bus import EventBus, EventType

class DispatchPipeline:
    def __init__(self, city_map: CityGridMap, vehicles: List[Vehicle]):
        self.city_map = city_map
        self.vehicles = vehicles
        
        # Core components
        self.event_bus = EventBus()
        self.nlp = NLPEngine()
        self.vision = VisionEngine(self.city_map)
        self.bayes = ProbabilisticEngine()
        self.logic = LogicEngine(self.city_map)
        self.rl_rebalancer = RLRebalancer(grid_shape=(len(city_map.grid), len(city_map.grid[0])))
        self.forecaster = DemandForecaster(grid_shape=(len(city_map.grid), len(city_map.grid[0])))

        # Configure listeners (subscribers)
        self._setup_event_listeners()

    def _setup_event_listeners(self):
        """Connect events to automatic handlers."""
        self.event_bus.subscribe(
            EventType.SAFETY_VIOLATION, 
            lambda data: print(f"[Pipeline Alert] Safety protocol triggered for task: {data.get('task_id')}")
        )

    def run_pipeline(
        self, 
        incident_id: str, 
        raw_text_report: str, 
        camera_image_mock: str, 
        current_hour: int = 14
    ) -> Dict[str, Any]:
        """
        Execute the complete end-to-end pipeline.
        """
        print("\n=== STARTING DISPATCH PIPELINE EXECUTION ===")

        # Step 1: NLP Processing
        incident = self.nlp.parse_report_to_incident(incident_id, raw_text_report)
        self.event_bus.publish(EventType.INCIDENT_REPORTED, incident)

        # Step 2: Vision Verification & Map Update
        verified = self.vision.verify_and_update_map(incident.location, camera_image_mock)
        if verified:
            incident.mark_verified(confidence=0.95, image_ref=camera_image_mock)
            self.event_bus.publish(EventType.INCIDENT_VERIFIED, incident)

        # Step 3: Probabilistic Traffic Inference
        delay_prob = self.bayes.calculate_traffic_delay_probability(
            has_nearby_accident=verified, 
            is_rush_hour=(7 <= current_hour <= 9 or 16 <= current_hour <= 19), 
            is_bad_weather=False
        )

        # Step 4: Convert Incident to Task & CSP Dispatch
        task = self.nlp.create_task_from_incident(incident)
        csp = CSPSolver(self.vehicles, [task])
        assignments = csp.solve_dispatch()

        execution_result = {}

        # Step 5: Routing & Logic Rules Verification
        if task.task_id in assignments:
            assigned_v = next(v for v in self.vehicles if v.id == assignments[task.task_id])
            planner = AStarPlanner(self.city_map)
            path, cost = planner.find_path(assigned_v.location, task.destination)

            # The target became traversable ('T') after vision inspection, so it is not a strict hazard zone.
            # A hazard zone exists only when the target cell itself is impassable ('X').
            # Note: if the destination is already 'X', the route is redirected to a neighboring cell,
            # but the area remains classified as hazardous (do not send non-rescue vehicles there).
            is_hazard_zone = not self.city_map.is_valid_cell(*task.destination)

            plan_approved = self.logic.validate_action_plan(
                vehicle=assigned_v,
                task=task,
                path=path,
                path_cost=cost,
                is_hazard=is_hazard_zone
            )

            if plan_approved:
                incident.status = IncidentStatus.DISPATCHED
                self.event_bus.publish(EventType.TASK_ASSIGNED, {"task_id": task.task_id, "vehicle_id": assigned_v.id})
                execution_result = {
                    "status": "SUCCESS",
                    "vehicle_assigned": assigned_v.id,
                    "path": path,
                    "cost": cost
                }
            else:
                self.event_bus.publish(EventType.SAFETY_VIOLATION, {"task_id": task.task_id})
                execution_result = {"status": "REJECTED_BY_SAFETY_RULES"}

        # Step 6: Autonomous Rebalancing for Idle Vehicles
        hotspots = self.forecaster.predict_high_demand_zones(current_hour=current_hour, top_n=2)
        assigned_v_ids = set(assignments.values())
        
        for v in self.vehicles:
            if v.id not in assigned_v_ids:
                new_pos = self.rl_rebalancer.rebalance_idle_vehicle(v.location, hotspots)
                v.location = new_pos
                self.event_bus.publish(EventType.REBALANCE_TRIGGERED, {"vehicle_id": v.id, "new_pos": new_pos})

        print("=== PIPELINE EXECUTION COMPLETED ===\n")
        return execution_result