package task40

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"
)

type Task struct {
	Dur string `json:"dur"`
}

var tasks []Task
var nextTask chan struct{}

func RunServer() {

	tasks = make([]Task, 0)
	nextTask = make(chan struct{})

	http.HandleFunc("/add", func(w http.ResponseWriter, r *http.Request) {
		if r.Method == "POST" {
			if err := r.ParseForm(); err != nil {
				fmt.Fprintf(w, "ParseForm() err: %v", err)
				return
			}
			timeDuration := r.FormValue("timeDuration")
			sync := r.FormValue("sync") // sync/async

			tasks = append(tasks, Task{
				Dur: timeDuration,
			})
			nextTask <- struct{}{}

			if sync == "sync" {

			} else if sync == "async" {

			} else {
				http.Error(w, "400 Bad request.", http.StatusBadRequest)
			}
		} else {
			http.Error(w, "405 Method not allowed.", http.StatusMethodNotAllowed)
		}
	})
	http.HandleFunc("/schedule", func(w http.ResponseWriter, r *http.Request) {
		if r.Method == "GET" {
			json.NewEncoder(w).Encode(tasks)
		} else {
			http.Error(w, "405 Method not allowed.", http.StatusMethodNotAllowed)
		}
	})
	http.HandleFunc("/time", func(w http.ResponseWriter, r *http.Request) {
		if r.Method == "GET" {
			sum := int64(0)
			for _, task := range tasks {
				dur, _ := time.ParseDuration(task.Dur)
				sum += dur.Milliseconds()
			}
			json.NewEncoder(w).Encode(struct {
				Time int64
			}{sum})
		}
	})
	go taskWork()
	http.ListenAndServe(":8089", nil)
}

var counter = 0

func taskWork() {
	_ = <-nextTask
	task := tasks[0]
	tasks = tasks[1:]
	dur, _ := time.ParseDuration(task.Dur)
	hardWork(dur, counter)
	counter++
}

func hardWork(dur time.Duration, i int) {
	log.Printf("Task %d start (dur: %s)\n", i, dur)
	time.Sleep(dur)
	log.Printf("Task %d stop\n", i)
}
