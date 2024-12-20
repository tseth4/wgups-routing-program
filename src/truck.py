from src.package_status import PackageStatus
from data_structures.hashmap import HashMap
from datetime import datetime, timedelta


class Truck:
    def __init__(self, id, capacity, address_mapping, speed=18, start_time="08:00:00"):
        self.id = id
        self.capacity = capacity
        self.speed = speed
        self.start_time = datetime.strptime(start_time, "%H:%M:%S")
        self.current_time = self.start_time
        self.current_location_index = 0  # Starting at hub
        self.total_distance = 0
        self.trips = []  # List of HashMaps for trips
        self.route = []  # 2D array of routes for each trip
        self.address_mapping = address_mapping

    def get_current_location_index(self):
        return self.current_location_index

    def set_current_location_index(self, index):
        self.current_location_index = index

    def get_speed(self):
        return self.speed

    def set_current_time(self, time):
        self.current_time = time

    def get_current_time(self):
        return self.current_time

    def get_capacity(self):
        return self.capacity

    def set_route(self, route):
        """Set the truck's delivery route."""
        self.route = route

    def __str__(self):
        """Return a human-readable string representation of the truck."""
        return f"Truck ID: {self.id}, Total Distance: {self.total_distance:.2f} miles, Current Time: {self.current_time.strftime('%H:%M:%S')}"

    def add_trip(self, packages):
        """Add a new trip to the truck."""
        if len(packages) > self.capacity:
            raise ValueError("Trip exceeds truck capacity.")
        self.trips.append(packages)

    def mark_trip_packages_en_route(self, trip):
        """
        Mark all packages in the given trip as EN_ROUTE.

        :param trip: HashMap containing packages for a specific trip.
        """
        for package_list in trip.values():
            for package in package_list:
                package.set_status(PackageStatus.EN_ROUTE)

    def _nearest_neighbor_for_trip(self, address_indices, adjacency_matrix, hub_index=0):
        """
        Optimize a single trip using the Nearest Neighbor algorithm.

        :param address_indices: List of address indices to visit in this trip.
        :param adjacency_matrix: 2D list representing distances between addresses.
        :param hub_index: Index of the hub in the adjacency matrix.
        :return: Tuple of (optimized route as list of indices, total distance).
        """
        if not address_indices:
            return [hub_index], 0  # If no addresses, return only the hub

        current_index = hub_index
        visited = set()
        route = [hub_index]
        # total_distance = 0

        while address_indices:
            nearest_distance = float('inf')
            nearest_index = None

            # Find the nearest unvisited address
            for address_index in address_indices:
                if address_index not in visited:
                    current_distance = float(
                        adjacency_matrix[current_index][address_index])
                    if current_distance < nearest_distance:
                        nearest_distance = current_distance
                        nearest_index = address_index
            if nearest_index is not None:
                route.append(nearest_index)
                # total_distance += nearest_distance
                visited.add(nearest_index)
                current_index = nearest_index
                # Remove from the list to avoid revisiting
                address_indices.remove(nearest_index)

        # Return to the hub
        distance_to_hub = float(adjacency_matrix[current_index][hub_index])
        # total_distance += distance_to_hub
        route.append(hub_index)
        # print(f"route from nna, truck id: {self.id} : {route}")

        # return route, total_distance
        return route

    def optimize_route(self, adjacency_matrix):
        # 2d array with routes
        self.route = []
        # Remeber we prepopoluate this considering edge cases
        for trip in self.trips:
            # Get all address indices in the trip
            trip_addresses = list(trip.keys())
            trip_route = self._nearest_neighbor_for_trip(
                trip_addresses, adjacency_matrix)

            self.route.append(trip_route)
            # self.total_distance += trip_distance

    def process_deliveries(self, adjacency_matrix, cutoff_time=None):
        if cutoff_time is None:
            # Default to EOD
            cutoff_time = datetime.strptime("17:00:00", "%H:%M:%S")
        hardcoded_time = datetime.strptime("10:20:00", "%H:%M:%S")

        # trip index is the hashmap index, trip is the HashMap
        for trip_index, trip in enumerate(self.trips):
            # Mark all packages in this trip as EN_ROUTE
            self.mark_trip_packages_en_route(trip)

            # Get the route for this trip
            trip_route = self.route[trip_index]
            current_time = self.current_time

            i = 1  # Start delivering from the first stop after hub
            while i < len(trip_route):
                prev_index = trip_route[i - 1]
                current_index = trip_route[i]

                # Calculate distance and travel time
                distance = float(adjacency_matrix[prev_index][current_index])
                travel_time = (distance / self.speed) * \
                    60  # Convert hours to minutes
                current_time += timedelta(minutes=travel_time)
                # print("current time updated: ", current_time)
                self.total_distance += distance

                # Hardcoded check for package 9 at 10:20 AM
                if current_time >= hardcoded_time:
                    # print("Hardcoded address update triggered")
                    for trip_idx, specific_trip in enumerate(self.trips):
                        for address, package_list in specific_trip.items():
                            for package in package_list:
                                if package.id == 9:  # Locate package 9
                                    # print(f"Package 9 found in trip {
                                    #       trip_idx} at address {address}")

                                    # Update address details
                                    new_address = "410 S State St"  # Replace with the actual address
                                    new_address_index = self.address_mapping.index(
                                        new_address)
                                    package.address = new_address
                                    package.address_index = new_address_index

                                    # Remove package from current trip
                                    package_list.remove(package)
                                    if not package_list:  # Remove address if no packages remain
                                        del specific_trip[address]

                                    # Add package to the updated trip
                                    specific_trip.merge_add(
                                        new_address_index, package)

                                    # Update the route for the trip
                                    if new_address_index not in self.route[trip_idx]:
                                        self.route[trip_idx].append(
                                            new_address_index)

                                    # print(f"Package 9 updated to {
                                    #       new_address} and moved to trip {trip_idx}")
                                    break  # Exit once package 9 is found and updated
                            else:
                                continue  # Continue outer loop if inner loop didn't break
                            break  # Break outermost loop if inner loop breaks

                # Check if cutoff time is exceeded
                if current_time > cutoff_time:
                    # print(f"Cutoff time reached. Returning to hub.")
                    return

                # Retrieve all packages for this address
                packages_at_address = trip.get(current_index)
                if packages_at_address:
                    # For each package at the address, mark as delivered or update
                    for package in packages_at_address:
                        package.mark_delivered(
                            self.id, current_time.strftime("%H:%M:%S"))

                    # Remove delivered packages from the trip
                    trip.delete(current_index)

                i += 1  # Only increment if no new address was added

            # Update truck's current time
            self.current_time = current_time
