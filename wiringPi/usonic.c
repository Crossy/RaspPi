#include <stdio.h>
#include <wiringPi.h>
#include <time.h>

#define BTN 0
#define TRIG 1
#define ECHO 2

#define DEBOUNCE 1000000	//1ms

void DelayMicrosecondsNoSleep (int delay_us);
void btnHandler(void);
void echoStartHandler(void);
void echoEndHandler(void);


long echoTime = 0;
int dist = -1;
struct timespec btn_time;
struct timespec start_time;
struct timespec end_time;

int main (void)
{
	printf("Starting demo\n");
	fflush(stdout);

	if (wiringPiSetup () == -1)
		return 1;

	pinMode(BTN, INPUT);
	pinMode(TRIG, OUTPUT);
	pinMode(ECHO, INPUT);

	digitalWrite(TRIG, LOW);

	wiringPiISR(BTN, INT_EDGE_RISING, &btnHandler);
	wiringPiISR(ECHO, INT_EDGE_RISING, &echoStartHandler);
	wiringPiISR(ECHO, INT_EDGE_FALLING, &echoEndHandler);

	while(1);
}

/**
 *On button push send trig signal
 **/
void btnHandler(void)
{
	//Debounce
	long prevTime = btn_time.tv_nsec;
	clock_gettime(CLOCK_MONOTONIC, &btn_time);
	if ((btn_time.tv_nsec - prevTime) < DEBOUNCE) {
		return;
	}

	//Send trigger pulse
	printf("BTN pushed\n");
	digitalWrite(TRIG, LOW);
	digitalWrite(TRIG, HIGH);
	DelayMicrosecondsNoSleep(20);
	digitalWrite(TRIG, LOW);
}

void echoStartHandler(void)
{
	//Get echo pulse start time
	clock_gettime(CLOCK_MONOTONIC, &start_time);
}

void echoEndHandler(void)
{
	//Get echo pulse end time and print calculated distance
	clock_gettime(CLOCK_MONOTONIC, &end_time);
	echoTime = (end_time.tv_nsec-start_time.tv_nsec) / 1000;
	dist = echoTime / 5.8; //dist in mm
	printf("dist = %d\n", dist);
}

//*****************************************************
//*****************************************************
//********** DELAY FOR # uS WITHOUT SLEEPING **********
//*****************************************************
//*****************************************************
//Using delayMicroseconds lets the linux scheduler decide to jump to another process.  Using this function avoids letting the
//scheduler know we are pausing and provides much faster operation if you are needing to use lots of delays.
void DelayMicrosecondsNoSleep (int delay_us)
{
	long int start_time;
	long int time_difference;
	struct timespec gettime_now;

	clock_gettime(CLOCK_REALTIME, &gettime_now);
	start_time = gettime_now.tv_nsec;		//Get nS value
	while (1)
	{
		clock_gettime(CLOCK_REALTIME, &gettime_now);
		time_difference = gettime_now.tv_nsec - start_time;
		if (time_difference < 0)
			time_difference += 1000000000;				//(Rolls over every 1 second)
		if (time_difference > (delay_us * 1000))		//Delay for # nS
			break;
	}
}
