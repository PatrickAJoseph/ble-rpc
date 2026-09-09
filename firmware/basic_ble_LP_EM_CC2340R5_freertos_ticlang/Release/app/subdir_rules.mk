################################################################################
# Automatically-generated file. Do not edit!
################################################################################

SHELL = cmd.exe

# Each subdirectory must supply rules for building sources it contributes
app/%.o: ../app/%.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler: "$<"'
	"C:/ti/ccs2100/ccs/tools/compiler/ti-cgt-armllvm_5.1.1.LTS/bin/tiarmclang.exe" -c @"C:/ti/simplelink_lowpower_f3_sdk_9_14_01_16/source/ti/ble/stack_util/config/build_components.opt" @"C:/ti/simplelink_lowpower_f3_sdk_9_14_01_16/source/ti/ble/stack_util/config/factory_config.opt"  -march=thumbv6m -mcpu=cortex-m0plus -mfloat-abi=soft -mlittle-endian -mthumb -Oz -I"F:/content_writing/ble-rpc/firmware/basic_ble_LP_EM_CC2340R5_freertos_ticlang" -I"F:/content_writing/ble-rpc/firmware/basic_ble_LP_EM_CC2340R5_freertos_ticlang/Release" -I"F:/content_writing/ble-rpc/firmware/basic_ble_LP_EM_CC2340R5_freertos_ticlang/app" -I"C:/ti/simplelink_lowpower_f3_sdk_9_14_01_16/source" -I"C:/ti/simplelink_lowpower_f3_sdk_9_14_01_16/source/ti" -I"C:/ti/simplelink_lowpower_f3_sdk_9_14_01_16/source/ti/common/cc26xx" -I"C:/ti/simplelink_lowpower_f3_sdk_9_14_01_16/source/ti/posix/ticlang" -I"C:/ti/simplelink_lowpower_f3_sdk_9_14_01_16/source/third_party/freertos/include" -I"C:/ti/simplelink_lowpower_f3_sdk_9_14_01_16/source/third_party/freertos/portable/GCC/ARM_CM0" -I"C:/ti/simplelink_lowpower_f3_sdk_9_14_01_16/kernel/freertos" -DICALL_NO_APP_EVENTS -DCC23X0 -DNVOCMP_NWSAMEITEM=1 -DNVOCMP_NVPAGES=6 -DFREERTOS -DNVOCMP_POSIX_MUTEX -gdwarf-3 -Wunused-function -ffunction-sections -MMD -MP -MF"app/$(basename $(<F)).d_raw" -MT"$(@)" -I"F:/content_writing/ble-rpc/firmware/basic_ble_LP_EM_CC2340R5_freertos_ticlang/Release/syscfg" -std=c99 $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo ' '


