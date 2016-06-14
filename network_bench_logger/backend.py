from flask import Flask, request, json
from kafka import SimpleProducer, KafkaClient

import lpgps

app = Flask(__name__)

try:
    kafka = KafkaClient('localhost:9092')
    producer = SimpleProducer(kafka)

    producer.send_messages(b'foo', b'test')
except:
    pass

@app.route("/submit/single_packet_metric", methods=["POST"])
def log_single_packet_metric():
    log_dict = {}

    try:
        log_dict['packet_ack_received'] = request.form['packet_ack_received']
        log_dict['ping_time_seconds'] = float(request.form['ping_time_s'])
        log_dict['sent_timestamp'] = float(request.form['send_timestamp'])
        log_dict['device_type'] = request.form['device_type']
        log_dict['carrier_name'] = request.form['carrier_name']
        log_dict['connection_type'] = request.form['connection_type']
        log_dict['allows_voip'] = request.form['allows_voip']
        log_dict['uuid'] = request.form['uuid']
        log_dict['trip_uid'] = request.form['trip_uid']
        log_dict['location'] = lpgps.get_train_coordinates(log_dict['trip_uid'], log_dict['sent_timestamp'])
    except Exception as e:
        return json.jsonify({'error': 'bad_params', 'exception' : str(e)})

    try:
        producer.send_messages(b'single_packet_points', (json.dumps(log_dict)).encode('utf-8'))
    except:
        pass

    return json.jsonify(log_dict['location'])


@app.route("/query/train_coordinates/", methods=["GET"])
def query_train_location():
    try:
        trip_uid = request.args['trip_uid']
        query_time_s = int(request.args['query_time_s'])
        return json.jsonify(lpgps.get_train_coordinates(trip_uid, query_time_s))
    except:
        return json.jsonify({'error': 'bad param'})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1337)
