echo "Spawning redis server instances"
redis-server ../Config/Replica1/redis.conf &
redis-server ../Config/Replica2/redis.conf &
redis-server ../Config/Replica3/redis.conf &
