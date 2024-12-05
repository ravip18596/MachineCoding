package Models

import "fmt"

type Person struct {
	id, name string
}

func CreatePerson(id, name string) *Person {
	return &Person{id: id, name: name}
}

type Group struct {
	id, name string
	Members  []string
}

func CreateGroup(id, name string, persons []*Person) *Group {
	g := Group{
		id:   id,
		name: name,
	}
	for _, person := range persons {
		g.Members = append(g.Members, person.id)
	}
	return &g
}

type Contribution struct {
	person   *Person
	shareAmt float64
}

func CreateContribution(person *Person, amt float64) *Contribution {
	AddPersonTxn(person, amt)
	return &Contribution{
		person:   person,
		shareAmt: amt,
	}
}

type Bill struct {
	totalAmount   float64
	desc          string
	group         *Group
	contributions []*Contribution
	paidBy        []*Contribution
}

func AddBill(desc string, group *Group, totalAmt float64, contributions, paidBy []*Contribution) *Bill {
	b := Bill{
		desc:          desc,
		group:         group,
		totalAmount:   totalAmt,
		contributions: contributions,
		paidBy:        paidBy,
	}
	for _,contrib := range contributions{
		AddGroupTxn(group, contrib.person, contrib.shareAmt)
	}
	for _,paid := range paidBy{
		AddGroupTxn(group, paid.person, paid.shareAmt)
	}
	return &b
}

var PersonWiseBalance map[*Person]float64

func InitMap(){
	PersonWiseBalance = make(map[*Person]float64)
	GroupWiseBalance = make(map[*Group]map[*Person]float64)
}

func AddPersonTxn(person *Person, amt float64) {
	if _,ok:= PersonWiseBalance[person]; !ok{
		PersonWiseBalance[person] = amt
	}else{
		PersonWiseBalance[person] += amt
	}
}

func ReturnPersonBalance(person *Person) float64{
	if _,ok := PersonWiseBalance[person]; !ok{
		return 0
	}
	return PersonWiseBalance[person]
}

var GroupWiseBalance map[*Group]map[*Person]float64

func AddGroupTxn(group *Group, person *Person, amt float64){
	if _,ok := GroupWiseBalance[group]; !ok {
		GroupWiseBalance[group] = make(map[*Person]float64)
		GroupWiseBalance[group][person] = amt
	}
	GroupWiseBalance[group][person] = amt
}

func PrintGroupBalance(group *Group){
	if _,ok := GroupWiseBalance[group];!ok{
		return
	}
	for person, amt := range GroupWiseBalance[group]{
		fmt.Println("person ",person.name, " has amt ",amt)
	}
}