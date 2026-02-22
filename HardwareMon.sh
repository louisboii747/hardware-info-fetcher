#!/bin/bash

VERSION="2.0.0"

MODE="summary"

# Colors
RED="\e[31m"
GREEN="\e[32m"
CYAN="\e[36m"
YELLOW="\e[33m"
RESET="\e[0m"

MAX_POINTS=50

cpu_history=()
mem_history=()
disk_history=()

clear_screen() {
clear
}

cpu_percent() {

awk -v RS="" '
{usage=($2+$4)*100/($2+$4+$5)}
END {printf "%d", usage}
' /proc/stat

}

mem_percent() {
free | awk '/Mem:/ {printf "%d", $3/$2 *100}'
}


disk_percent() {
df / | awk 'NR==2 {print $5}' | tr -d %
}

bar() {

value=$1
width=50

filled=$((value*width/100))

printf "["

for ((i=0;i<filled;i++))
do
printf "#"
done

for ((i=filled;i<width;i++))
do
printf " "
done

printf "] %s%%" "$value"

}

graph() {

arr=("$@")

for v in "${arr[@]}"
do

height=$((v/5))

printf "%2s|" "$v"

for ((i=0;i<height;i++))
do
printf "#"
done

echo

done

}

add_history() {

cpu_history+=($(cpu_percent))
mem_history+=($(mem_percent))
disk_history+=($(disk_percent))

if [ ${#cpu_history[@]} -gt $MAX_POINTS ]
then

cpu_history=("${cpu_history[@]:1}")
mem_history=("${mem_history[@]:1}")
disk_history=("${disk_history[@]:1}")

fi

}

alerts() {

cpu=$(cpu_percent)
mem=$(mem_percent)

if ((cpu>90))
then
echo -e "${RED}CPU HIGH${RESET}"
fi

if ((mem>90))
then
echo -e "${RED}MEMORY HIGH${RESET}"
fi

}

summary() {

cpu=$(cpu_percent)
mem=$(mem_percent)
disk=$(disk_percent)

echo -e "${CYAN}=== SYSTEM SUMMARY ===${RESET}"

printf "CPU  "
bar $cpu
echo

printf "MEM  "
bar $mem
echo

printf "DISK "
bar $disk
echo

echo

alerts

}

full() {

summary

echo

echo -e "${CYAN}=== CPU GRAPH ===${RESET}"

graph "${cpu_history[@]}"

echo

echo -e "${CYAN}=== MEMORY GRAPH ===${RESET}"

graph "${mem_history[@]}"

echo

echo -e "${CYAN}=== DISK GRAPH ===${RESET}"

graph "${disk_history[@]}"

echo

echo -e "${CYELLOW}Top Processes${RESET}"

ps -eo comm,%cpu,%mem \
--sort=-%cpu | head -6

echo

echo -e "${CYAN}Temperatures${RESET}"

sensors 2>/dev/null | grep Core

echo

echo -e "${CYAN}GPU${RESET}"

lspci | grep -Ei "VGA|3D"

}

while true
do

clear_screen

add_history

if [ "$MODE" = "summary" ]
then
summary
else
full
fi

echo

echo "HardwareMon Lite v$VERSION"

echo "Press:"
echo "s = summary"
echo "f = full"
echo "q = quit"

read -t 1 -n 1 key

case "$key" in

s)
MODE="summary"
;;

f)
MODE="full"
;;

q)
exit
;;

esac

done
