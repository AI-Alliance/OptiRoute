import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from 'src/environments/environment';
import { Vehicle } from '../models/Vehicle';
import { PlaceMarker } from '../models/PlaceMarker';
import { v4 as uuidv4 } from 'uuid';

@Injectable({
  providedIn: 'root'
})
export class TaskService {

  constructor(private httpClient: HttpClient) { 
    
  }

  sendTask(vehicles: Vehicle[], places: PlaceMarker[], matrix: google.maps.DistanceMatrixResponse){

    console.log(matrix);
    let placesToSend = [];

    for(let i = 0; i < places.length; i++){
      let place = places[i];
      placesToSend.push({place_id: place.uuid, place_index: i, demand: place.demand});
    }

    let vehiclesToSend = vehicles.map((v)=> {return {vehicle_id: v.uuid, capacity: v.capacity}});
    
    
    let matrixToSend = [];

    for (const row of matrix.rows) {

      let elements: number[] = row.elements.map(e=> e.duration.value)

      matrixToSend.push({elements: elements})
    }



    // matrixToSend.forEach((r )=> r.elements.map(e=> e.duration.value))
    return this.httpClient.post(environment.backendAddress +'/tasks',{
      task_id: uuidv4(),
      places: placesToSend,
      vehicles: vehiclesToSend,
      rows: matrixToSend
    });
  }
}
