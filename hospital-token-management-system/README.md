# Hospital Token Management System

A beginner-friendly DSA internal project written in C. It runs locally in the terminal and demonstrates FIFO queues and emergency-first scheduling.

## Features
- Register regular patients
- Register emergency patients
- Serve the next patient (emergency queue first)
- Display the waiting list
- Unique patient token numbers
- Input validation and a maximum of 50 waiting patients

## Requirements
- C compiler (GCC or Clang)
- macOS, Linux, or Windows with a C compiler

## Compile and run on macOS/Linux
```bash
gcc -std=c11 -Wall -Wextra hospital.c -o hospital
./hospital
```

On macOS, if the compiler is missing, install Apple Command Line Tools:
```bash
xcode-select --install
```

## DSA concepts
- Queue and FIFO
- Enqueue and dequeue operations
- Arrays and structures in C
- Modular programming with functions
- Emergency-first scheduling across two queues

## Limitations
Patient records are held in memory and are cleared when the program exits. This is an educational demo, not a real patient-management system.
