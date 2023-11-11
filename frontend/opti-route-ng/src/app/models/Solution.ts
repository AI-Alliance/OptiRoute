export interface Solution{
    id: string, 
    task_id: string, 
    vehicles: {
        route:{demand: number, place_id: string, place_index: number}[],
        vehicle_id: string
    }[]
}