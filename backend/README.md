# Docker
docker build -t g-backend .
docker run -p 5000:5000 g-backend

# FLASK SERVER
## activate venv
venv\Scripts\activate
## Run the server
flask run

### Run with debug (automatically reload)
flask run --debug

### Update dependencies

pip3 freeze > requirements.txt

### ENDPOINTS

GET, POST
http://127.0.0.1:5000/tasks

GET
http://127.0.0.1:5000/solutions

GET
http://127.0.0.1:5000/solutions/774cca52-dd96-42b1-bb88-5c422ff30ce8

### POST REQUEST

{
    "task_id": "774cca52-dd96-42b1-bb88-5c422ff30ce8",
    "places":[
        {
            "place_id" : "694cca52-dd96-42b1-bb88-5c422ff30ce8",
            "place_index" : 0,
            "demand": 0
        },
        {
            "place_id" : "2007d679-0013-4310-b14e-744ff8844eec",
            "place_index" : 1,
            "demand": 3
        },
        {
            "place_id" : "b4681e02-5625-406c-9410-5efa5dc34479",
            "place_index" : 1,
            "demand": 2
        }
    ],
    "vehicles":[
        {
            "vehicle_id": "490091c1-c7ea-4fed-8a1d-b2fd1a244384",
            "capacity": 1
        },
        {
            "vehicle_id": "6bfb00e5-fd53-4d95-97d7-15058c5f1d94",
            "capacity": 3
        }
    ],
    "rows" : [
        {
            "elements":[0, 10, 56]
        },
        {
            "elements":[10, 0, 17]
        },
        {
            "elements":[56, 17, 0]
        }
    ]
}
### RESPONSE

{
    "vehicles":[
         {
            "vehicle_id": "490091c1-c7ea-4fed-8a1d-b2fd1a244384",
            "route": [
                {
                    "place_id" : "694cca52-dd96-42b1-bb88-5c422ff30ce8",
                    "place_index" : 0,
                    "demand": 0
                },
                {
                    "place_id" : "2007d679-0013-4310-b14e-744ff8844eec",
                    "place_index" : 1,
                    "demand": 3
                },
                {
                    "place_id" : "694cca52-dd96-42b1-bb88-5c422ff30ce8",
                    "place_index" : 0,
                    "demand": 0
                }
            ]
        },
        {
            "vehicle_id": "6bfb00e5-fd53-4d95-97d7-15058c5f1d94",
            "route": [
                {
                    "place_id" : "694cca52-dd96-42b1-bb88-5c422ff30ce8",
                    "place_index" : 0,
                    "demand": 0
                },
                {
                    "place_id" : "b4681e02-5625-406c-9410-5efa5dc34479",
                    "place_index" : 1,
                    "demand": 2
                },
                {
                    "place_id" : "694cca52-dd96-42b1-bb88-5c422ff30ce8",
                    "place_index" : 0,
                    "demand": 0
                }
            ]
        }
    ]
}