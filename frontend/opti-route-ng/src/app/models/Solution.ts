export interface Solution{
    id: string, 
    task_id: string, 
    vehicles: {

        route:{
            duration_sum: number,
            places:{demand: number, place_id: string, place_index: number}[],
        }
        
        vehicle_id: string
    }[],
    algorithm: string,
    vehiclesC: number[], 
    placesD: number[],
    stats: {max: number, avg: number, sum: number}
}