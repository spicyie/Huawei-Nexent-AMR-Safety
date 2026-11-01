import requests
import json

# ==========================================
# 1. MCP TOOLS (Deterministic Math)
# ==========================================
def calculate_required_distance(speed, target_speed=0.5, max_decel=1.0, delay=0.2, margin=0.5):
    if speed <= target_speed:
        return margin
    response_dist = speed * delay
    brake_dist = (speed**2 - target_speed**2) / (2 * max_decel)
    return response_dist + brake_dist + margin

# ==========================================
# 2. STRATEGIC LLM (The Nexent Agent)
# ==========================================
class StrategicAgent:
    def decide_mode(self, speed, distance):
        req_dist = calculate_required_distance(speed)
        
        prompt = f"""
        You are the Strategic Planner for an AMR in a factory.
        Current speed: {speed:.2f} m/s. Distance to Human Work Zone: {distance:.2f} m.
        The mathematical required distance to brake safely is {req_dist:.2f} m.
        
        RULES:
        - If distance > {req_dist:.2f} m, choose NORMAL_MODE.
        - If distance <= {req_dist:.2f} m, choose SAFE_APPROACH_MODE.
        
        Decide the operating mode. Reply ONLY with JSON:
        {{"mode": "NORMAL_MODE"}} or {{"mode": "SAFE_APPROACH_MODE"}}
        """
        try:
            res = requests.post("http://localhost:11434/api/generate", 
                                json={"model": "llama3.1:8b", "prompt": prompt, "stream": False, "format": "json"}, 
                                timeout=10)
            parsed_mode = json.loads(res.json()["response"].strip()).get("mode", "NORMAL_MODE")
            
            # --- NEW DEBUG PRINT ---
            # This shows you the LLM's "thought process" without cluttering the main log
            print(f"    [LLM Thought] Dist: {distance:.1f}m <= Req: {req_dist:.2f}m? -> Selected: {parsed_mode}")
            # -----------------------
            
            return parsed_mode
        except Exception as e:
            print(f"    [LLM Error] {e}. Defaulting to SAFE_APPROACH_MODE.")
            return "SAFE_APPROACH_MODE" # Fail-safe

# ==========================================
# 3. LOCAL DETERMINISTIC CONTROLLER
# ==========================================
class LocalController:
    def __init__(self):
        self.current_mode = "NORMAL_MODE"
        self.cruise_speed = 2.0
        self.safe_speed = 0.5

    def update_mode(self, mode):
        self.current_mode = mode

    def calculate_acceleration(self, current_speed):
        target_speed = self.cruise_speed if self.current_mode == "NORMAL_MODE" else self.safe_speed
        error = target_speed - current_speed
        
        # Tighter deadband: Only stop if within 0.05 of target
        if abs(error) < 0.05: 
            return 0.0 
        
        if error > 0:
            return min(0.5, error) # Accelerate smoothly
        else:
            return max(-1.0, error) # Decelerate smoothly

# ==========================================
# 4. INDEPENDENT SAFETY SUPERVISOR
# ==========================================
class SafetySupervisor:
    def override_control(self, requested_accel, current_speed, distance):
        req_dist = calculate_required_distance(current_speed)
        
        # If we are within the danger zone, override and force braking
        if distance <= req_dist:
            if requested_accel > 0:
                return -1.0, "OVERRIDE: Emergency braking (Inside danger zone)."
        return requested_accel, None

# ==========================================
# 5. SIMULATION ENGINE
# ==========================================
if __name__ == "__main__":
    agent = StrategicAgent()
    controller = LocalController()
    safety = SafetySupervisor()
    
    pos, boundary, speed, dt = 30.0, 12.0, 2.0, 0.2
    steps = 0
    
    print("--- STARTING v6.0 HIERARCHICAL SIMULATION ---")
    
    while pos > boundary and steps < 100:
        dist = pos - boundary
        
        # STRATEGIC LOOP: Poll the LLM every single step to prevent blind spots
        mode = agent.decide_mode(speed, dist)
        controller.update_mode(mode)
            
        # DETERMINISTIC CONTROL LOOP: Runs every step
        requested_accel = controller.calculate_acceleration(speed)
        
        # SAFETY SUPERVISOR: The final authority
        final_accel, override = safety.override_control(requested_accel, speed, dist)
        
        print(f"[Step {steps:02}] Dist: {dist:5.2f}m | Mode: {controller.current_mode:<18} | Speed: {speed:4.2f} | Accel: {final_accel:4.2f} {override if override else ''}")
        
        # PHYSICS UPDATE
        new_speed = max(0.0, speed + final_accel * dt)
        dx = (speed * dt) + (0.5 * final_accel * (dt**2))
        if dx < 0: dx = 0
        pos -= dx
        speed = new_speed
        steps += 1

    print("\n--- SIMULATION COMPLETE ---")
    if pos <= boundary:
        print(f"Result: PASS ✅ (Crossed boundary safely)")
    else:
        print(f"Result: FAIL ❌ (Stalled at {pos:.2f}m)")
        
    print(f"Final Position: {pos:.2f}m (Boundary: {boundary}m)")
    print(f"Final Speed: {speed:.2f} m/s")
    print(f"Total Steps: {steps} (Time: {steps * dt:.1f}s)")