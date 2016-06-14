#cd ~/kafka**; bin/kafka-topics.sh --replication-factor 1 --partitions 1 --zookeeper localhost --topic single_packet_points --create; cd ..
curl -XPUT 'http://localhost:9200/single_packet_points/' -d '{
    "settings" : {
        "number_of_shards" : 3,
        "number_of_replicas" : 0
    }
}'
# Mapping
