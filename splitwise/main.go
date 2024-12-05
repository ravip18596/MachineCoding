package main

import (
	"fmt"
	"splitwise/Models"
)

func main() {
	Models.InitMap()
	person1 := Models.CreatePerson("person1@xyz.com", "Person1")
	person2 := Models.CreatePerson("person2@xyz.com", "Person2")
	person3 := Models.CreatePerson("person3@xyz.com", "Person3")

	group1 := Models.CreateGroup("group1", "Group 1", []*Models.Person{person1, person2})
	group2 := Models.CreateGroup("group2", "Group 2", []*Models.Person{person2, person3})

	contrib1 := Models.CreateContribution(person1, -100)
	contrib2 := Models.CreateContribution(person2, -200)
	bill1Contib := []*Models.Contribution{contrib1, contrib2}
	contrib3 := Models.CreateContribution(person1, 300.0)
	bill1paidBy := []*Models.Contribution{contrib3}

	bill1 := Models.AddBill("Bill 1", group1, 300, bill1Contib, bill1paidBy)

	contrib4 := Models.CreateContribution(person1, -250)
	contrib5 := Models.CreateContribution(person2, -250)
	bill2Contib := []*Models.Contribution{contrib4, contrib5}
	contrib6 := Models.CreateContribution(person2, 500.0)
	bill2paidBy := []*Models.Contribution{contrib6}

	bill2 := Models.AddBill("Bill 2", group1, 500, bill2Contib, bill2paidBy)

	contrib7 := Models.CreateContribution(person2, -10)
	contrib8 := Models.CreateContribution(person3, -90)
	bill3Contib := []*Models.Contribution{contrib7, contrib8}
	contrib9 := Models.CreateContribution(person3, 100.0)
	bill3paidBy := []*Models.Contribution{contrib9}

	bill3 := Models.AddBill("Bill 3", group2, 100, bill3Contib, bill3paidBy)

	fmt.Println("person1 balance is ", Models.ReturnPersonBalance(person1))
	fmt.Println("person2 balance is ", Models.ReturnPersonBalance(person2))
	fmt.Println("person3 balance is ", Models.ReturnPersonBalance(person3))

	Models.PrintGroupBalance(group1)
	Models.PrintGroupBalance(group2)

	fmt.Println(bill1, bill2, bill3)

}
