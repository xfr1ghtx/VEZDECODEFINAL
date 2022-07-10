package task20

import (
	"bufio"
	"log"
	"os"
	"strings"
	"sync"
	"time"
)

func Task20() {
	file, err := os.Open("tasks/input.txt")
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	counter := 0
	var wg sync.WaitGroup
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if len(line) == 0 {
			continue
		}
		dur, err := time.ParseDuration(line)
		if err != nil {
			log.Fatal(err)
		}
		go hardWork(dur, counter, &wg)
		counter++
	}
	if err := scanner.Err(); err != nil {
		log.Fatal(err)
	}

	wg.Wait()
}

func hardWork(dur time.Duration, i int, wg *sync.WaitGroup) {
	wg.Add(1)
	defer wg.Done()

	log.Printf("Task %d start (dur: %s)\n", i, dur)
	time.Sleep(dur)
	log.Printf("Task %d stop\n", i)
}
