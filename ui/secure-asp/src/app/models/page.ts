export interface Page<T> {
    items: T[];
    total: number;
    page: number;
    size: number;
    pages: number;
    }

export enum Order {
    ASC = 'asc',
    DESC = 'desc'
}