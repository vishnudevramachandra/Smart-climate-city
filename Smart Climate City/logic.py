"""
Smart Intersection Logic Engine for Project EcoFlow
Decides traffic light timing and routing based on predicted traffic and air quality
"""

from config import (
    DEFAULT_CAPACITY_THRESHOLD,
    STANDARD_GREEN_DURATION,
    EXTENDED_GREEN_DURATION,
    EMERGENCY_PM10_THRESHOLD,
    EMERGENCY_PM25_THRESHOLD
)


class SmartIntersection:
    """
    Smart traffic intersection that optimizes for both traffic flow and air quality.

    Features:
    - Congestion management: Extends green lights during high traffic
    - Climate override: Suggests rerouting when air pollution is hazardous
    """

    def __init__(self, name, capacity_threshold=DEFAULT_CAPACITY_THRESHOLD):
        """
        Initialize a smart intersection.

        Parameters:
        - name: Name of the intersection (e.g., "Heilbronn Center")
        - capacity_threshold: Traffic volume (cars/hr) that triggers congestion mode
        """
        self.name = name
        self.capacity = capacity_threshold
        self.state = "NORMAL"
        self.green_light_duration = STANDARD_GREEN_DURATION
        self.decision_history = []

    def decide(self, predicted_traffic, current_aqi):
        """
        Make a traffic control decision based on predicted traffic and air quality.

        Parameters:
        - predicted_traffic: Predicted traffic volume (vehicles per hour)
        - current_aqi: Current air quality index - PM10 level (µg/m³)

        Returns:
        - str: Status message describing the decision
        """
        traffic_status = "NORMAL"
        air_status = "GOOD"

        # ====================================================================
        # RULE 1: CONGESTION MANAGEMENT
        # ====================================================================
        # If predicted traffic exceeds capacity, extend green light duration
        if predicted_traffic > self.capacity:
            self.green_light_duration = EXTENDED_GREEN_DURATION
            traffic_status = "HEAVY"
        else:
            self.green_light_duration = STANDARD_GREEN_DURATION
            traffic_status = "NORMAL"

        # ====================================================================
        # RULE 2: CLIMATE OVERRIDE (The Hackathon Winner Feature!)
        # ====================================================================
        # If air pollution exceeds emergency threshold, prioritize public health
        # over traffic flow by suggesting rerouting
        if current_aqi > EMERGENCY_PM10_THRESHOLD:
            air_status = "HAZARDOUS"
            self.state = "⛔ REROUTING (Toxic Air)"
            action = "REROUTE"
            reason = f"PM10 level ({current_aqi:.1f} µg/m³) exceeds safe limit"

        elif traffic_status == "HEAVY":
            air_status = "ACCEPTABLE"
            self.state = f"🟢 MAX FLOW (Green: {self.green_light_duration}s)"
            action = "EXTEND_GREEN"
            reason = f"High traffic volume ({predicted_traffic:.0f} cars/hr)"

        else:
            air_status = "GOOD"
            self.state = f"🟢 STANDARD (Green: {self.green_light_duration}s)"
            action = "NORMAL"
            reason = "Normal traffic and air quality"

        # Log decision
        decision = {
            'traffic': predicted_traffic,
            'aqi': current_aqi,
            'traffic_status': traffic_status,
            'air_status': air_status,
            'action': action,
            'green_duration': self.green_light_duration,
            'reason': reason
        }
        self.decision_history.append(decision)

        return self.state

    def get_action_description(self):
        """
        Get a detailed description of the current action being taken.

        Returns:
        - str: Action description for display
        """
        if "REROUTE" in self.state:
            return "⚠️ Digital signs set to 'DETOUR' - Protecting public health"
        elif "MAX FLOW" in self.state:
            return "⚡ Green light cycle extended - Maximizing traffic flow"
        else:
            return "✅ Standard operation - All systems normal"

    def get_color_code(self):
        """
        Get color code for visual display.

        Returns:
        - str: Color name (red, yellow, green)
        """
        if "REROUTE" in self.state:
            return "red"
        elif "MAX FLOW" in self.state:
            return "yellow"
        else:
            return "green"

    def reset(self):
        """Reset the intersection to default state."""
        self.state = "NORMAL"
        self.green_light_duration = STANDARD_GREEN_DURATION
        self.decision_history = []


class TrafficNetwork:
    """
    Manage multiple smart intersections in a network.
    """

    def __init__(self):
        self.intersections = {}

    def add_intersection(self, name, capacity_threshold=DEFAULT_CAPACITY_THRESHOLD):
        """Add a new intersection to the network."""
        self.intersections[name] = SmartIntersection(name, capacity_threshold)
        return self.intersections[name]

    def get_intersection(self, name):
        """Get an intersection by name."""
        return self.intersections.get(name)

    def get_network_status(self):
        """Get status of all intersections in the network."""
        return {name: intersection.state
                for name, intersection in self.intersections.items()}


def calculate_health_impact(aqi_pm10):
    """
    Calculate health impact based on PM10 levels (WHO guidelines).

    Parameters:
    - aqi_pm10: PM10 level in µg/m³

    Returns:
    - dict: Health impact information
    """
    if aqi_pm10 <= 20:
        level = "Excellent"
        color = "#00C853"  # Green
        message = "Air quality is excellent. Ideal for outdoor activities."
    elif aqi_pm10 <= 40:
        level = "Good"
        color = "#64DD17"  # Light green
        message = "Air quality is good. Safe for all activities."
    elif aqi_pm10 <= 50:
        level = "Moderate"
        color = "#FFD600"  # Yellow
        message = "Air quality is acceptable for most people."
    elif aqi_pm10 <= 100:
        level = "Unhealthy"
        color = "#FF6D00"  # Orange
        message = "Sensitive groups should limit outdoor activities."
    else:
        level = "Hazardous"
        color = "#DD2C00"  # Red
        message = "Health warning! Everyone should avoid outdoor activities."

    return {
        'level': level,
        'color': color,
        'message': message,
        'pm10': aqi_pm10
    }


if __name__ == "__main__":
    """
    Test the logic engine with different scenarios
    """
    print("=" * 70)
    print("⚙️  PROJECT ECOFLOW - LOGIC ENGINE TEST")
    print("=" * 70)

    intersection = SmartIntersection("Heilbronn Center", capacity_threshold=120)

    test_scenarios = [
        {
            'name': "Scenario 1: Normal Conditions",
            'traffic': 50,
            'aqi': 20
        },
        {
            'name': "Scenario 2: Rush Hour",
            'traffic': 150,
            'aqi': 25
        },
        {
            'name': "Scenario 3: Toxic Air Emergency",
            'traffic': 80,
            'aqi': 65
        }
    ]

    for scenario in test_scenarios:
        print(f"\n{scenario['name']}")
        print("-" * 70)
        print(f"Input: Traffic={scenario['traffic']} cars/hr, PM10={scenario['aqi']} µg/m³")

        status = intersection.decide(scenario['traffic'], scenario['aqi'])

        print(f"Output: {status}")
        print(f"Action: {intersection.get_action_description()}")
        print(f"Green Light Duration: {intersection.green_light_duration}s")

        health = calculate_health_impact(scenario['aqi'])
        print(f"Health Impact: {health['level']} - {health['message']}")

    print("\n" + "=" * 70)
    print("✅ LOGIC ENGINE TEST COMPLETE!")
    print("=" * 70)
