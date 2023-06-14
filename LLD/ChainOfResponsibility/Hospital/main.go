package main

import (
	"fmt"
)

// handler interface

type Department interface {
	execute(*Person)
	setNext(Department)
}

type Reception struct {
	next Department
}

func (r *Reception) execute(p *Person) {
	if p.registrationDone {
		fmt.Printf("%s: Patient registration is done \n", p.name)
		r.next.execute(p)
		return
	}
	fmt.Println("Reception registering patient")
	p.registrationDone = true
	r.next.execute(p)
}

func (r *Reception) setNext(next Department) {
	r.next = next
}

type Doctor struct {
	next Department
}

func (d *Doctor) execute(p *Person) {
	if p.doctorCheckupDone {
		fmt.Println("Patient doctor checkup done")
		d.next.execute(p)
		return
	}
	fmt.Println("Patient is being examined by doctor")
	p.doctorCheckupDone = true
	d.next.execute(p)
}

func (d *Doctor) setNext(next Department) {
	d.next = next
}

type Medical struct {
	next Department
}

func (m *Medical) execute(p *Person) {
	if p.gotMedicine {
		fmt.Println("Patient got medicine.")
		m.next.execute(p)
		return
	}
	fmt.Println("Patient is getting medicine.")
	p.gotMedicine = true
	m.next.execute(p)
}

func (m *Medical) setNext(next Department) {
	m.next = next
}

type Cashier struct {
	next Department
}

func (c *Cashier) execute(p *Person) {
	if p.paymentDone {
		fmt.Println("Patient has completed payment")
		return
	}
	fmt.Println("Cashier is receiving payment from patient")
	p.paymentDone = true
}

func (c *Cashier) setNext(next Department) {
	c.next = next
}

type Person struct {
	name              string
	registrationDone  bool
	doctorCheckupDone bool
	gotMedicine       bool
	paymentDone       bool
}

func main() {
	cashier := &Cashier{}
	medical := &Medical{}
	medical.setNext(cashier)
	doctor := &Doctor{}
	doctor.setNext(medical)
	reception := &Reception{}
	reception.setNext(doctor)

	p := &Person{name: "Ravi"}
	reception.execute(p)

	reception.execute(p)
}
