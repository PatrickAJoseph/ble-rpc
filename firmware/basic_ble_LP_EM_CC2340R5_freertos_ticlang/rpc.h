#ifndef __RPC_H__
#define __RPC_H__

#include <stdint.h>
#include <stdlib.h>

#include <ti/posix/ticlang/semaphore.h>

typedef void (*rpc_callback)(uint8_t id, void* data, size_t length);

#define RPC_CALLBACK_DEFINE(__name)      \
    void __name(uint8_t id, void* data, size_t length)

#define RPC_CALLBACK_ENTRY( __id, __callback)   \
    {                                           \
        .id = __id,                             \
        .callback = __callback,                 \
    }

#define RPC_CALLBACK_ENTRY_END  RPC_CALLBACK_ENTRY( 0x00, NULL ) 

#define RPC_CALLBACK_TABLE_DEFINE(_name)      \
    struct rpc_callback_entry _name [] =

struct rpc_callback_entry {
    uint8_t id;
    rpc_callback callback;
};


typedef struct rpc_callback_entry* rpc_callback_table;

struct rpc {
    sem_t commandReceivedSem;
    rpc_callback_table callback_table;
    void* command;
    uint8_t command_id;
    size_t command_length;
    void* response;
    uint8_t response_id;
    size_t response_length;
    void* notification;
    uint8_t notification_id;
    size_t notification_length;
};

extern void RPC_init(struct rpc* rpc, rpc_callback_table callback_table);
extern void RPC_waitForCommand(struct rpc* rpc);
extern void RPC_processCommands(struct rpc* rpc);
extern void RPC_sendNotification(struct rpc* rpc, uint8_t id, void* data, size_t length);

#endif /* __RPC_H__ */