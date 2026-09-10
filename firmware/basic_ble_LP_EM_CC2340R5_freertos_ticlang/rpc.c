#include "rpc.h"

#include <ti/posix/ticlang/semaphore.h>
#include <ti/posix/ticlang/pthread.h>

#include "ti/ble/stack_util/icall/app/icall.h"
#include "ti/ble/stack_util/health_toolkit/assert.h"
#include "ti/ble/stack_util/bcomdef.h"

extern bStatus_t __RPC_sendResponse(uint8_t id, uint8_t* data, size_t length);
extern bStatus_t __RPC_sendNotification(uint8_t id, uint8_t* data, size_t length);

void RPC_init(struct rpc* rpc, rpc_callback_table callback_table)
{
    rpc->callback_table = callback_table;
    rpc->command = NULL;
    rpc->command_id = 0;
    rpc->command_length = 0;
    rpc->response = NULL;
    rpc->response_id = 0;
    rpc->response_length = 0;
    rpc->notification = NULL;
    rpc->notification_id = 0;
    rpc->notification_length = 0;

    (void)sem_init(&rpc->commandReceivedSem, 0, 0);
}

void RPC_processCommands(struct rpc* rpc)
{
    struct rpc_callback_entry* entry;

    entry = &rpc->callback_table[0];

    while(entry->callback != NULL)
    {
        if( rpc->command_id == entry->id )
        {
            rpc->response_id = rpc->command_id;
            entry->callback( rpc->command_id, &rpc->command[0], rpc->command_length );
            __RPC_sendResponse( rpc->command_id, &(((uint8_t*)rpc->response)[0]), rpc->response_length);
        }

        entry++;
    }
}

void RPC_waitForCommand(struct rpc* rpc)
{
    sem_wait(&rpc->commandReceivedSem);
}

void RPC_sendNotification(struct rpc* rpc, uint8_t id, void* data, size_t length)
{
    __RPC_sendNotification(id, (uint8_t*)data, length);
}