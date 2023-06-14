package main

import (
	"fmt"
	"strings"
	"time"
)

type Logger interface {
	log(level, message string)
	setNext(Logger)
}
type InfoLogger struct {
	next Logger
}

func (i *InfoLogger) log(level, msg string) {
	if strings.ToLower(level) == "info" {
		fmt.Printf("%s:[%s] %s \n", strings.ToUpper(level), time.Now().Format("2006-01-02 03:04:05"), msg)
		return
	}
	i.next.log(level, msg)
}

func (i *InfoLogger) setNext(next Logger) {
	i.next = next
}

type DebugLogger struct {
	next Logger
}

func (i *DebugLogger) log(level, msg string) {
	if strings.ToLower(level) == "debug" {
		fmt.Printf("%s:[%s] %s \n", strings.ToUpper(level), time.Now().Format("2006-01-02 03:04:05"), msg)
		return
	}
	i.next.log(level, msg)
}

func (d *DebugLogger) setNext(next Logger) {
	d.next = next
}

type ErrorLogger struct {
	next Logger
}

func (e *ErrorLogger) log(level, msg string) {
	if strings.ToLower(level) == "error" {
		fmt.Printf("%s:[%s] %s \n", "ERROR", time.Now().Format("2006-01-02 03:04:05"), msg)
		return
	}
	e.next.log(level, msg)
}

func (e *ErrorLogger) setNext(next Logger) {
	e.next = next
}

type Log struct {
	log Logger
}

func main() {
	err := &ErrorLogger{}
	debug := &DebugLogger{}
	debug.setNext(err)
	info := &InfoLogger{}
	info.setNext(debug)

	l := &Log{log: info}
	l.log.log("info", "This is info msg")
	l.log.log("ERROR", "This is an exception")
	l.log.log("DEBUG", "This is debug log")
}
