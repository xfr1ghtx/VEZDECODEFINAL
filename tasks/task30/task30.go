package task30

import (
	"bufio"
	"fmt"
	"log"
	"os"
	"strings"
	"sync"
	"time"
)

func Task30() {
	file, err := os.Open("tasks/input.txt")
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	counter := 0
	var wg sync.WaitGroup
	var maxGoroutines int
	fmt.Println("Write a integer:")
	_, err = fmt.Scan(&maxGoroutines)
	if err != nil {
		log.Fatalln("write a Integer")
		return
	}
	guard := make(chan struct{}, maxGoroutines)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if len(line) == 0 {
			continue
		}
		dur, err := time.ParseDuration(line)
		if err != nil {
			log.Fatal(err)
		}
		guard <- struct{}{}
		go func(dur time.Duration, i int) {
			wg.Add(1)

			hardWork(dur, i)

			<-guard
			wg.Done()
		}(dur, counter)

		counter++
	}
	if err := scanner.Err(); err != nil {
		log.Fatal(err)
	}

	wg.Wait()
}

func hardWork(dur time.Duration, i int) {
	log.Printf("Task %d start (dur: %s)\n", i, dur)
	time.Sleep(dur)
	log.Printf("Task %d stop\n", i)
}
