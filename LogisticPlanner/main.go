package main

import "fmt"

type Vehicle struct {
	ID          int
	Capacity    int
	CurrentLoad int
	Route       []string
}

type Item struct {
	Id          int
	Volume      int
	Priority    int
	Destination string
}

type Warehouse struct {
	Name string
}

type LogisticPlanner struct {
	Vehicles   []Vehicle
	Items      []Item
	Warehouses []Warehouse
}

func (lp *LogisticPlanner) AssignItemsToVehicles() {
	for _, item := range lp.Items {
		for i, vehicle := range lp.Vehicles {
			if vehicle.CurrentLoad+item.Volume <= vehicle.Capacity {
				lp.Vehicles[i].CurrentLoad += item.Volume
				lp.Vehicles[i].Route = append(lp.Vehicles[i].Route, item.Destination)
			}
		}
	}
}

func (lp *LogisticPlanner) GenerateReport() {
	var totalDispatchedItems, totalDispatchedVolume, totalCapacity int
	var dePrioritizedItems []Item

	for _, vehicle := range lp.Vehicles {
		totalDispatchedItems += len(vehicle.Route)
		totalDispatchedVolume += vehicle.CurrentLoad
		totalCapacity += vehicle.Capacity
	}

	for _, item := range lp.Items {
		if !contains(lp.Vehicles, item.Destination) {
			dePrioritizedItems = append(dePrioritizedItems, item)
		}
	}

	wastedVolumePercentage := float64(totalCapacity-totalDispatchedVolume) / float64(totalCapacity) * 100

	fmt.Println("Vehicles dispatched:", len(lp.Vehicles))
	fmt.Println("Items dispatched:", totalDispatchedItems)
	fmt.Printf("Volume wasted percentage: %.2f%%\n", wastedVolumePercentage)
	fmt.Println("Items deprioritized:", len(dePrioritizedItems))
}

func contains(vehicles []Vehicle, destination string) bool {
	for _, vehicle := range vehicles {
		for _, r := range vehicle.Route {
			if r == destination {
				return true
			}
		}
	}
	return false
}

func main() {
	// Case 1
	vehicles := []Vehicle{
		{
			ID:       1,
			Capacity: 10,
		},
	}
	items := []Item{
		{
			Id:          1,
			Volume:      5,
			Priority:    4,
			Destination: "A",
		},
		{
			Id:          2,
			Volume:      8,
			Priority:    2,
			Destination: "B",
		},
	}

	planner := LogisticPlanner{
		Vehicles: vehicles,
		Items:    items,
	}
	planner.AssignItemsToVehicles()
	planner.GenerateReport()

	fmt.Println()

	//Case 2
	vehicles = []Vehicle{
		{
			ID:       1,
			Capacity: 10,
		},
		{
			ID:       2,
			Capacity: 20,
		},
	}
	items = []Item{
		{
			Id:          1,
			Volume:      20,
			Priority:    4,
			Destination: "A",
		},
		{
			Id:          2,
			Volume:      5,
			Priority:    10,
			Destination: "B",
		},
	}
	planner2 := LogisticPlanner{
		Vehicles: vehicles,
		Items:    items,
	}
	planner2.AssignItemsToVehicles()
	planner2.GenerateReport()
}
