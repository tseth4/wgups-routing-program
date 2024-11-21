from src.package_status import PackageStatus


class Truck:
    def __init__(self, id, capacity):
        """
        Initialize the Truck object.

        :param id: Unique identifier for the truck.
        :param capacity: Maximum number of packages the truck can carry.
        """
        self.id = id
        self.capacity = capacity
        self.current_location = None  # Starting location (e.g., hub)
        self.route = []  # List of addresses/nodes to visit
        self.packages = []  # List of Package objects
        self.total_distance = 0  # Total distance traveled

    def assign_package(self, package):
        """Assign a package to the truck."""
        if len(self.packages) < self.capacity:
            package.set_status(PackageStatus.EN_ROUTE)
            self.packages.append(package)
            return True
        return False

    def set_route(self, route):
        """Set the truck's delivery route."""
        self.route = route

    def deliver_package(self, address):
        """Simulate delivering a package."""
        self.packages = [
            pkg for pkg in self.packages if pkg.address != address]

    def update_location(self, new_location, distance):
        """Move the truck to a new location and update distance."""
        self.current_location = new_location
        self.total_distance += distance

    def reset(self):
        """Reset the truck for a new simulation."""
        self.current_location = None
        self.route = []
        self.packages = []
        self.total_distance = 0

    def __str__(self):
        """Return a human-readable string representation of the truck."""
        package_ids = [pkg.id for pkg in self.packages]
        route_str = " -> ".join(self.route) if self.route else "No route assigned"
        return (
            f"Truck ID: {self.id}\n"
            f"Capacity: {self.capacity}\n"
            f"Current Location: {self.current_location}\n"
            f"Total Distance Traveled: {self.total_distance} miles\n"
            f"Route: {route_str}\n"
            f"Assigned Packages: {package_ids}"
        )

    def process_deliveries():
        pass

    @staticmethod
    def nearest_neighbor(matrix, addresses, start_index=0):
        """
        Nearest Neighbor Algorithm using an adjacency matrix.

        :param matrix: 2D list representing the adjacency matrix.
        :param nodes: List of node names corresponding to the matrix indices.
        :param start_index: Index of the starting node.
        :return: A tuple containing the route (list of nodes) and total distance.
        """
        n = len(matrix)
        visited = [False] * n
        route = [start_index]
        total_distance = 0

        current_index = start_index
        visited[current_index] = True

        for _ in range(n - 1):
            nearest_distance = float('inf')
            nearest_index = None

            for next_index in range(n):
                current_dist = float(matrix[current_index][next_index])
                if not visited[next_index] and current_dist < nearest_distance:
                    nearest_distance = current_dist
                    nearest_index = next_index

            if nearest_index is not None:
                route.append(nearest_index)
                total_distance += nearest_distance
                visited[nearest_index] = True
                current_index = nearest_index

        # Optionally return to the starting node
        total_distance += float(matrix[current_index][start_index])
        route.append(start_index)

        # Convert route indices to node names
        route_names = [addresses[i] for i in route]
        return route_names, total_distance

    def optimize_route(self, matrix, nodes, hub_index=0):
        """
        Optimize the route for this truck using nearest_neighbor.

        :param matrix: 2D list representing the adjacency matrix.
        :param nodes: List of node names corresponding to the matrix indices.
        :param hub_index: Starting index for the hub.
        """
        if not self.packages:
            print(f"Truck {self.id} has no packages to deliver.")
            return

        # Get package addresses and corresponding indices
        package_addresses = [package.get_address() for package in self.packages]
        # indices = [nodes.index(addr) for addr in package_addresses]

        # Use nearest_neighbor to calculate the optimal route
        route, distance = Truck.nearest_neighbor(matrix, nodes, hub_index)

        # Update truck's route and total distance
        self.route = route
        self.total_distance = distance
        print(f"Truck {self.id} optimized route: {self.route}")
        print(f"Total distance for Truck {
              self.id}: {self.total_distance} miles")