

#include "ti/ble/stack_util/bcomdef.h"
#include "ti/ble/host/gap/gapgattserver.h"
#include "ti/ble/host/gap/gap_advertiser.h"
#include <app_main.h>
#include "ti/ble/host/gapbondmgr/gapbondmgr.h"
#include "ti_ble_config.h"
#include "ti/ble/app_util/framework/bleapputil_api.h"

// The GAP profile role
uint8_t profileRole = GAP_PROFILE_PERIPHERAL;
// GAP GATT Service (GGS) parameters
uint8_t attDeviceName[GAP_DEVICE_NAME_LEN]= "Basic BLE project";

uint8_t pRandomAddress[B_ADDR_LEN] = {0};

// Initiate selected profiles
void init_profiles(){
 }
/*********************************************************************
 * Bond Manager Configuration
 */

gapBondParams_t gapBondParams = {
    .pairMode             = GAPBOND_PAIRING_MODE_WAIT_FOR_REQ,
    .mitm                 = true,
    .ioCap                = GAPBOND_IO_CAP_DISPLAY_ONLY,
    .bonding              = true,
    .secureConnection     = GAPBOND_SECURE_CONNECTION_ALLOW,
    .authenPairingOnly    = false,
    .autoSyncAL           = false,
    .eccReGenPolicy       = 0,
    .KeySize              = 16,
    .removeLRUBond        = false,
    .KeyDistList          = GAPBOND_KEYDIST_CENCKEY | GAPBOND_KEYDIST_CIDKEY | GAPBOND_KEYDIST_CSIGN | GAPBOND_KEYDIST_PENCKEY | GAPBOND_KEYDIST_PIDKEY | GAPBOND_KEYDIST_PSIGN,
    .eccDebugKeys         = false,
    .eraseBondWhileInConn = false,
    .sameIrkAction        = GAPBOND_SAME_IRK_UPDATE_BOND_REC
};

uint8_t pairMode                =    GAPBOND_PAIRING_MODE_WAIT_FOR_REQ;
uint8_t mitm                    =    true;
uint8_t ioCap                   =    GAPBOND_IO_CAP_DISPLAY_ONLY;
uint8_t bonding                 =    true;
uint8_t secureConnection        =    GAPBOND_SECURE_CONNECTION_ALLOW;
uint8_t authenPairingOnly       =    false;
uint8_t autoSyncAL              =    false;
uint8_t eccReGenPolicy          =    0;
uint8_t KeySize                 =    16;
uint8_t removeLRUBond           =    false;
uint8_t KeyDistList             =    GAPBOND_KEYDIST_CENCKEY | GAPBOND_KEYDIST_CIDKEY | GAPBOND_KEYDIST_CSIGN | GAPBOND_KEYDIST_PENCKEY | GAPBOND_KEYDIST_PIDKEY | GAPBOND_KEYDIST_PSIGN;
uint8_t eccDebugKeys            =    false;
uint8_t allowDebugKeys          =    true;
uint8_t eraseBondWhileInConn    =    false;
uint8_t sameIrkAction           =    GAPBOND_SAME_IRK_UPDATE_BOND_REC;

void setBondManagerParameters()
{
    GAPBondMgr_SetParameter(GAPBOND_PAIRING_MODE, sizeof(uint8_t), &pairMode);
    GAPBondMgr_SetParameter(GAPBOND_MITM_PROTECTION, sizeof(uint8_t), &mitm);
    GAPBondMgr_SetParameter(GAPBOND_IO_CAPABILITIES, sizeof(uint8_t), &ioCap);
    GAPBondMgr_SetParameter(GAPBOND_BONDING_ENABLED, sizeof(uint8_t), &bonding);
    GAPBondMgr_SetParameter(GAPBOND_SECURE_CONNECTION, sizeof(uint8_t), &secureConnection);
    // Set Authenticated Pairing Only mode
    GAPBondMgr_SetParameter(GAPBOND_AUTHEN_PAIRING_ONLY, sizeof(uint8_t), &authenPairingOnly);
    // Set Auto Acceptlist Sync
    GAPBondMgr_SetParameter(GAP_ADV_AL_POLICY_ANY_REQ, sizeof(uint8_t), &autoSyncAL);
    GAPBondMgr_SetParameter(GAPBOND_ECCKEY_REGEN_POLICY, sizeof(uint8_t), &eccReGenPolicy);
    GAPBondMgr_SetParameter(GAPBOND_KEYSIZE, sizeof(uint8_t), &KeySize);
    GAPBondMgr_SetParameter(GAPBOND_LRU_BOND_REPLACEMENT, sizeof(uint8_t), &removeLRUBond);
    GAPBondMgr_SetParameter(GAPBOND_KEY_DIST_LIST, sizeof(uint8_t), &KeyDistList);
    // Set Secure Connection Debug Keys
    GAPBondMgr_SetParameter(GAPBOND_SC_HOST_DEBUG, sizeof(uint8_t), &eccDebugKeys);
    // Set Allow Debug Keys
    GAPBondMgr_SetParameter(GAPBOND_ALLOW_DEBUG_KEYS, sizeof(uint8_t), &allowDebugKeys);
    // Set the Erase bond While in Active Connection Flag
    GAPBondMgr_SetParameter(GAPBOND_ERASE_BOND_IN_CONN, sizeof(uint8_t), &eraseBondWhileInConn);
    GAPBondMgr_SetParameter(GAPBOND_SAME_IRK_OPTION, sizeof(uint8_t), &sameIrkAction);
}


GapAdv_params_t advParams1 = {
  .eventProps =   GAP_ADV_PROP_CONNECTABLE | GAP_ADV_PROP_LEGACY | GAP_ADV_PROP_SCANNABLE,
  .primIntMin =   160,
  .primIntMax =   160,
  .primChanMap =  GAP_ADV_CHAN_ALL,
  .peerAddrType = PEER_ADDRTYPE_PUBLIC_OR_PUBLIC_ID,
  .peerAddr =     { 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa },
  .filterPolicy = GAP_ADV_AL_POLICY_ANY_REQ,
  .txPower =      GAP_ADV_TX_POWER_NO_PREFERENCE,
  .primPhy =      GAP_ADV_PRIM_PHY_1_MBPS,
  .secPhy =       GAP_ADV_SEC_PHY_1_MBPS,
  .sid =          0
};

uint8_t advData1[] =
{
  0x02,
  GAP_ADTYPE_FLAGS,
  GAP_ADTYPE_FLAGS_BREDR_NOT_SUPPORTED | GAP_ADTYPE_FLAGS_GENERAL,

  0x03,
  GAP_ADTYPE_16BIT_MORE,
  LO_UINT16(0xfff0),
  HI_UINT16(0xfff0),



};


uint8_t scanResData1[] =
{
  0x12,
  GAP_ADTYPE_LOCAL_NAME_COMPLETE,
  'B',
  'a',
  's',
  'i',
  'c',
  ' ',
  'B',
  'L',
  'E',
  ' ',
  'p',
  'r',
  'o',
  'j',
  'e',
  'c',
  't',

  0x02,
  GAP_ADTYPE_POWER_LEVEL,
  0,


  0x05,
  GAP_ADTYPE_PERIPHERAL_CONN_INTERVAL_RANGE,
  LO_UINT16(80),
  HI_UINT16(80),
  LO_UINT16(104),
  HI_UINT16(104),

};



/*********************************************************************
 * @fn      BleConfig_initAdvSets
 *
 * @brief   Initializes all advertising sets configured by SysConfig.
 *          This function initializes each set using BLEAppUtil_initAdvSet.
 *          The advHandles array will be populated with handles for each
 *          advertising set upon successful initialization.
 *
 * @param [out] advHandles - Array to store handles for each advertising set.
 *                           Assumed of size @ref BLE_CONFIG_NUM_ADV_SETS.
 * @param [out] advHandlesStatus - Array to store handles statuses for each 
 *                                 advertising set.
 *
 * @return  None
 */
void BleConfig_initAdvSets(uint8_t* advHandles, uint8_t* advHandlesStatus)
{
    bStatus_t status = SUCCESS;

    if (advHandles == NULL)
    {
      status = FAILURE;
      
      /* assign FAILURE to the first handle status */
      if(advHandlesStatus != NULL)
      {
        *advHandlesStatus = status;
      }
    }
    else
    {
        AdvSetInfo_t advSetsInfo[BLE_CONFIG_NUM_ADV_SETS] = {
            {
              .advData = advData1,
              .advDataLen = sizeof(advData1),
              .scanRspData = scanResData1,
              .scanRspDataLen = sizeof(scanResData1),
              .advParams = &advParams1
            },
        };

        for (uint8_t i = 0; i < BLE_CONFIG_NUM_ADV_SETS; i++)
        {
            BLEAppUtil_AdvInit_t advSetInitParamsSet;
            advSetInitParamsSet.advDataLen      = advSetsInfo[i].advDataLen;
            advSetInitParamsSet.advData         = advSetsInfo[i].advDataLen == 0 ? NULL : advSetsInfo[i].advData;
            advSetInitParamsSet.scanRespDataLen = advSetsInfo[i].scanRspDataLen;
            advSetInitParamsSet.scanRespData    = advSetsInfo[i].scanRspDataLen == 0 ? NULL : advSetsInfo[i].scanRspData;
            advSetInitParamsSet.advParam        = advSetsInfo[i].advParams;

            status = BLEAppUtil_initAdvSet(&advHandles[i], &advSetInitParamsSet);

            if(advHandlesStatus != NULL)
            {
              advHandlesStatus[i] = status;
            }
        }
    }
}

/*********************************************************************
 * @fn      BleConfig_startAdvSets
 *
 * @brief   Starts all advertising sets using the provided handles.
 *          This function iterates through the array of advertising set handles
 *          and starts each advertising set with default start parameters,
 *          using @ref BLEAppUtil_advStart function.
 *          It also stores the status returned for each handle in a given array.
 *
 * @param advHandles - Pointer to array of advertising set handles.
 * @param [out] advHandlesStatus - Pointer to an array to store the status
 *                    returned from BLEAppUtil_advStart, for each given handle.
 *                    If initialized to NULL, this pointer won't be used.
 * @param size - Number of advertising set handles in both arrays.
 *
 * @return  None
 */
void BleConfig_startAdvSets(uint8_t* advHandles, uint8_t* advHandlesStatus, uint8_t size)
{
    bStatus_t status;

    BLEAppUtil_AdvStart_t advSetStartParams =
    {
        .enableOptions         = GAP_ADV_ENABLE_OPTIONS_USE_MAX,
        .durationOrMaxEvents   = 0
    };

    if (advHandles != NULL)
    {
      for (uint8_t i = 0; i < size; i++)
      {
          status = BLEAppUtil_advStart(advHandles[i], &advSetStartParams);

          if (advHandlesStatus != NULL)
          {
              advHandlesStatus[i] = status;
          }
      }
    }
}

/*********************************************************************
 * @fn      BleConfig_stopAdvSets
 *
 * @brief   Stops all advertising sets using the provided handles.
 *          This function iterates through the array of advertising set handles
 *          and stops each advertising set using @ref BLEAppUtil_advStop function.
 *          It also stores the status returned for each handle in a given array.
 *
 * @param advHandles - Pointer to array of advertising set handles.
 * @param [out] advHandlesStatus - Pointer to an array to store the status
 *                    returned from BLEAppUtil_advStop, for each given handle.
 *                    If initialized to NULL, this pointer won't be used.
 * @param size - Number of advertising set handles in both arrays.
 *
 * @return  None
 */
void BleConfig_stopAdvSets(uint8_t* advHandles, uint8_t* advHandlesStatus, uint8_t size)
{
    bStatus_t status;

    if (advHandles != NULL)
    {
      for (uint8_t i = 0; i < size; i++)
      {
          status = BLEAppUtil_advStop(advHandles[i]);

          if (advHandlesStatus != NULL)
          {
              advHandlesStatus[i] = status;
          }
      }
    }
}

