package main

type AccountStatus int
type PaymentStatus int
type OrderStatus int

const (
	ACTIVE AccountStatus = iota
	INACTIVE
	BLOCKED
)

const (
	PENDING PaymentStatus = iota
	COMPLETED
	DECLINED
	CANCELLED
	REFUNDED
)

type Address struct {
	streetAddress string
	city          string
	state         string
	zipCode       string
}

func CreateAddress(streetAddress, city, state, zipCode string) *Address {
	return &Address{
		streetAddress: streetAddress,
		city:          city,
		state:         state,
		zipCode:       zipCode,
	}
}

type CreditCard struct {
	cardNumber string
}

type ElectronicBankTransfer struct {
	bankAccountNumber string
}

type Account struct {
	userName      string
	password      string
	accountStatus AccountStatus
	name          string
	address       Address
	email         string
	phone         string
	creditCards   []CreditCard
	bankAccounts  []ElectronicBankTransfer
}

func (a Account) addProduct(product Product) {

}

type Admin struct {
	Account
}

type Member struct {
	Account
}

func (m Member) placeOrder(order Order) OrderStatus {
	return order.orderStatus
}

type Customer struct {
}

type Guest struct {
}

func (g Guest) registerAccount(username, password string) *Account {
	return &Account{
		userName:      username,
		password:      password,
		accountStatus: ACTIVE,
	}
}

type System struct {
}

type ProductCategory struct {
	name        string
	description string
}

type ProductReview struct {
	review string
	rating int
}

type Product struct {
	id
}

type Item struct {
	quantity int
}

type Cart struct {
}

type Order struct {
	orderStatus OrderStatus
}

func CreateOrder() *Order {
	return &Order{}
}

type Payment struct {
	amount        float64
	paymentStatus PaymentStatus
}
