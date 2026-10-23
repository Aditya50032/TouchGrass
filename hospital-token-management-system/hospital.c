#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_PATIENTS 50
#define NAME_LEN 50
#define REASON_LEN 100
#define INPUT_LEN 256

typedef struct {
    int token;
    char name[NAME_LEN];
    int age;
    char reason[REASON_LEN];
} Patient;

typedef struct {
    Patient items[MAX_PATIENTS];
    int count;
} Queue;

void clearInputLine(void) {
    int ch;
    while ((ch = getchar()) != '\n' && ch != EOF) {
    }
}

int readInt(const char *prompt, int min, int max) {
    char input[INPUT_LEN];
    char *end;
    long value;

    while (1) {
        printf("%s", prompt);

        if (fgets(input, sizeof(input), stdin) == NULL) {
            printf("\nInput ended. Exiting.\n");
            exit(EXIT_SUCCESS);
        }

        if (strchr(input, '\n') == NULL && !feof(stdin)) {
            clearInputLine();
        }

        value = strtol(input, &end, 10);

        if (end == input) {
            printf("Please enter a valid number.\n");
            continue;
        }

        while (*end == ' ' || *end == '\t' ||
               *end == '\n' || *end == '\r') {
            end++;
        }

        if (*end != '\0') {
            printf("Invalid input. Enter a number only.\n");
            continue;
        }

        if (value < min || value > max) {
            printf("Enter a value between %d and %d.\n", min, max);
            continue;
        }

        return (int)value;
    }
}

void readText(const char *prompt, char *destination, size_t capacity) {
    char input[INPUT_LEN];
    size_t length;
    size_t i;

    while (1) {
        printf("%s", prompt);

        if (fgets(input, sizeof(input), stdin) == NULL) {
            printf("\nInput ended. Exiting.\n");
            exit(EXIT_SUCCESS);
        }

        if (strchr(input, '\n') == NULL && !feof(stdin)) {
            clearInputLine();
        }

        input[strcspn(input, "\r\n")] = '\0';
        length = strlen(input);
        i = 0;

        while (i < length && (input[i] == ' ' || input[i] == '\t')) {
            i++;
        }

        if (i == length) {
            printf("This field cannot be empty.\n");
            continue;
        }

        snprintf(destination, capacity, "%s", input);
        return;
    }
}

int enqueue(Queue *queue, const Patient *patient) {
    if (queue->count >= MAX_PATIENTS) {
        return 0;
    }

    queue->items[queue->count] = *patient;
    queue->count++;
    return 1;
}

int dequeue(Queue *queue, Patient *patient) {
    int i;

    if (queue->count == 0) {
        return 0;
    }

    *patient = queue->items[0];

    for (i = 1; i < queue->count; i++) {
        queue->items[i - 1] = queue->items[i];
    }

    queue->count--;
    return 1;
}

void registerPatient(Queue *queue, int *nextToken, const char *type) {
    Patient patient;

    patient.token = *nextToken;
    printf("\n--- Register %s Patient ---\n", type);
    readText("Enter patient name: ", patient.name, sizeof(patient.name));
    patient.age = readInt("Enter patient age (1-120): ", 1, 120);
    readText("Enter reason for visit: ", patient.reason, sizeof(patient.reason));

    if (enqueue(queue, &patient)) {
        (*nextToken)++;
        printf("\nPatient registered successfully!\n");
        printf("Token number: %d\n", patient.token);
        printf("Patient type: %s\n", type);
    } else {
        printf("This queue is full.\n");
    }
}

void displayQueue(const Queue *queue, const char *title) {
    int i;

    printf("\n--- %s ---\n", title);
    if (queue->count == 0) {
        printf("No patients waiting.\n");
        return;
    }

    printf("%-8s %-20s %-6s %s\n", "Token", "Name", "Age", "Reason");
    printf("--------------------------------------------------\n");

    for (i = 0; i < queue->count; i++) {
        printf("%-8d %-20.20s %-6d %s\n",
               queue->items[i].token,
               queue->items[i].name,
               queue->items[i].age,
               queue->items[i].reason);
    }
}

void displayWaitingList(const Queue *emergencyQueue, const Queue *regularQueue) {
    printf("\n========== WAITING LIST ==========\n");
    displayQueue(emergencyQueue, "Emergency Patients");
    displayQueue(regularQueue, "Regular Patients");
    printf("\nTotal patients waiting: %d\n",
           emergencyQueue->count + regularQueue->count);
}

void serveNextPatient(Queue *emergencyQueue, Queue *regularQueue) {
    Patient patient;

    if (dequeue(emergencyQueue, &patient)) {
        printf("\nServing EMERGENCY patient.\n");
    } else if (dequeue(regularQueue, &patient)) {
        printf("\nServing regular patient.\n");
    } else {
        printf("\nNo patients are waiting.\n");
        return;
    }

    printf("Token number: %d\n", patient.token);
    printf("Name: %s\n", patient.name);
    printf("Age: %d\n", patient.age);
    printf("Reason: %s\n", patient.reason);
    printf("Patient has been served successfully.\n");
}

int main(void) {
    Queue regularQueue = {0};
    Queue emergencyQueue = {0};
    int nextToken = 1001;
    int choice;

    while (1) {
        printf("\n====================================\n");
        printf("   HOSPITAL TOKEN MANAGEMENT SYSTEM\n");
        printf("====================================\n");
        printf("1. Register Regular Patient\n");
        printf("2. Register Emergency Patient\n");
        printf("3. Serve Next Patient\n");
        printf("4. Display Waiting List\n");
        printf("5. Exit\n");
        printf("====================================\n");

        choice = readInt("Enter your choice (1-5): ", 1, 5);

        switch (choice) {
            case 1:
            case 2: {
                int totalWaiting = regularQueue.count + emergencyQueue.count;

                if (totalWaiting >= MAX_PATIENTS) {
                    printf("\nWaiting list is full. Cannot register more patients.\n");
                    break;
                }

                if (choice == 1) {
                    registerPatient(&regularQueue, &nextToken, "Regular");
                } else {
                    registerPatient(&emergencyQueue, &nextToken, "Emergency");
                }
                break;
            }

            case 3:
                serveNextPatient(&emergencyQueue, &regularQueue);
                break;

            case 4:
                displayWaitingList(&emergencyQueue, &regularQueue);
                break;

            case 5:
                printf("\nThank you for using the system!\n");
                return 0;
        }
    }
}
