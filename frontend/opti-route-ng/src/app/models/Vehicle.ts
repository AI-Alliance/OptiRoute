import { v4 as uuidv4 } from 'uuid';


export class Vehicle{
    uuid: string;
    capacity: number;
    constructor(capacity: number){
        this.capacity = capacity;
        this.uuid = uuidv4();
    }
}