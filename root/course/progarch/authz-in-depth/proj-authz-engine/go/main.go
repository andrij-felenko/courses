package main

import (
	"fmt"
	"strings"
)

type RelationTuple struct {
	ObjectID  string
	Relation  string
	SubjectID string
}

type EvalContext struct {
	CurrentTimeHour  int
	AllowedStartHour int
	AllowedEndHour   int
}

type RebacAbacEngine struct {
	tuples map[string][]RelationTuple
}

func NewEngine() *RebacAbacEngine {
	return &RebacAbacEngine{tuples: make(map[string][]RelationTuple)}
}

func (e *RebacAbacEngine) AddTuple(obj, relation, subject string) {
	e.tuples[obj] = append(e.tuples[obj], RelationTuple{
		ObjectID:  obj,
		Relation:  relation,
		SubjectID: subject,
	})
}

func (e *RebacAbacEngine) CheckRebac(subject, relation, obj string, visited map[string]bool) bool {
	stateKey := obj + "#" + relation + "@" + subject
	if visited[stateKey] {
		return false
	}
	visited[stateKey] = true

	tuples := e.tuples[obj]
	for _, t := range tuples {
		if t.Relation != relation {
			continue
		}
		if t.SubjectID == subject {
			return true
		}
		if strings.Contains(t.SubjectID, "#") {
			parts := strings.Split(t.SubjectID, "#")
			if e.CheckRebac(subject, parts[1], parts[0], visited) {
				return true
			}
		}
	}
	return false
}

func (e *RebacAbacEngine) Evaluate(subject, action, obj string, ctx EvalContext) bool {
	visited := make(map[string]bool)
	if !e.CheckRebac(subject, action, obj, visited) {
		return false
	}
	if ctx.CurrentTimeHour < ctx.AllowedStartHour || ctx.CurrentTimeHour > ctx.AllowedEndHour {
		return false
	}
	return true
}

func main() {
	engine := NewEngine()
	engine.AddTuple("home:101", "owner", "user:alice")
	engine.AddTuple("camera:704", "parent", "home:101")
	engine.AddTuple("camera:704", "viewer", "home:101#owner")

	ctxDay := EvalContext{CurrentTimeHour: 14, AllowedStartHour: 8, AllowedEndHour: 22}
	fmt.Println("Day access:", engine.Evaluate("user:alice", "viewer", "camera:704", ctxDay))

	ctxNight := EvalContext{CurrentTimeHour: 23, AllowedStartHour: 8, AllowedEndHour: 22}
	fmt.Println("Night access:", engine.Evaluate("user:alice", "viewer", "camera:704", ctxNight))
}
