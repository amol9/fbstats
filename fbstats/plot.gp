#set terminal png size size
set output '| display png:-'
set term png font "Ubuntu, 9" size size
set boxwidth 0.3
set style fill solid
unset key
set yrange [0:]
set title title font "Ubuntu, 10"
plot '<cat' using 1:xtic(2) with boxes lc rgb "#3B5998"

