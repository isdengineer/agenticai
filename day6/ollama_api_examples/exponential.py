import time
retry=1
while True:
    try:
        raise Exception("Some exception")

    except Exception as e:
        print("exception",e)
        print("Retrying after",retry)
        time.sleep(retry)
        retry =retry + 5
