package task10

import (
	"bufio"
	"log"
	"os"
	"strings"
	"time"
)

func Task10() {
	file, err := os.Open("tasks/input.txt")
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	counter := 0
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if len(line) == 0 {
			continue
		}
		dur, err := time.ParseDuration(line)
		if err != nil {
			log.Fatal(err)
		}
		hardWork(dur, counter)
		counter++
	}

	if err := scanner.Err(); err != nil {
		log.Fatal(err)
	}
}

func hardWork(dur time.Duration, i int) {
	log.Printf("Task %d start (dur: %s)\n", i, dur)
	time.Sleep(dur)
	log.Printf("Task %d stop\n", i)
}
