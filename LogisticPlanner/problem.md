# Quantum Logistics
Your Trusted Logistics Service
> (We’ll get it there... Or maybe.... We'll see)

## Description
The warehouse is a busy place. Lots of vehicles and items of different sizes come and go, all the time.
You will get to manage how items are dispatched on the vehicles.
Design and implement a toy version of logistic planner where we can plan item dispatch via road transportation between warehouses.


## Requirements

1. The warehouse will have some vehicles stationed and new vehicles can be added as and when they come in.
2. Each Vehicle can be uniquely identified and has a max capacity  (represented by an integer).
3. Items are also arriving at the warehouse all the time which needs to be dispatched to a different warehouse via some vehicle.
4. Each Item needs to be dispatched, and
   - has volume ( represented by an integer).
   - has a priority ( represented by an integer).
   - is to be dispatched to a different warehouse identified by a name (represented by a String).
5. Warehouse is just a name and not an exact address.
   - Items going to different warehouses must NOT be dispatched together by the same vehicle.
6. Priority defines which items should be prioritized over the others. Items with priority 0 have the highest priority. The range of priority values can be assumed to be [0, 2^31].
   - If due to any constraints the item cannot be prioritized, it can be deprioritized until the constraints allow it to be dispatched. Such constraints can be - items are too big for the vehicle, no vehicle available etc.
   - An item is considered de-prioritized, if you end up dispatching other low priority items before this high priority item due to any constraints.  
   - Such de-prioritized items should be counted and reported in the final report. See below.
7. We need a way to generate a report about:
   - Count of vehicles dispatched
   - Count of items dispatched
   - Volume Wasted in % : (1- (Total Volume Dispatched / Total Capacity Of Dispatched Vehicle)) * 100
   - Count of Deprioritized items: Defined as the count of items that couldn't be dispatched due to any reason.
     * The report is always from the beginning of time.


```text
Case 1:

> Vehicles: [{max_vol=10}]
> Items:   [{vol=5, priority=4, dispatch="A"}, {vol=8, priority=2, dispatch="B"}]

// Command:
> dispatch
> generateReport

// Output:
vehicles dispatched = 1
items disaptched = 1
volume wasted percentage = 20
items deprioritized = 0

// Explaination:
There was only 1 vehicle in standby and its capacity cannot hold both items. Among the 2 items item(second item in list) needs to be prioritized and we see that it can indeed be dispatched. The same is seen in the output. No items were depioritized here.
```

```text
Case 2:

> Items: [{vol=20,priority=4, dispatch="A"}, {vol=5, priority=10, dispatch="B"}]
> Vehicles: [{max_vol=10}]

// Command:
> dispatch
> generateReport

// Output:
vehicles dispatched = 1
items disaptched = 1
volume wasted percentage = 50
items deprioritized = 1

// Explanation:
There was 1 vehicle in standby, but is not enough to hold the high priority item. Hence it was marked as "deprioritized" and is being counted in the report. The other low priority item was instead dispatched and is also shown in the report.

// Input: lets add a vehicle and dispatch again
> Vehicles: [{max_vol=20}]

// Command:
> dispatch
> generateReport

// Output:
vehicles dispatched = 2
items disaptched = 2
volume_wasted_pct = 16.77
items_deprioritized = 1

// Explaination:
Now the vehicle was added, we can now dispatch the deprioritized item with that vehicle. The same can be seen in the report.
```