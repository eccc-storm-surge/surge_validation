#ord_soumet= -cpus 256 -t 21600 -jn surge-validation -mach ppp8

. /home/olh001/.profile_python3

work_dir=${1:-"/home/olh001/Python/surge_validation"}
pyscript=${2?"Path to the script should be passed as second arg"}


echo "Launching ${pyscript} in ${work_dir}"

cd ${work_dir}

python -u ${pyscript}