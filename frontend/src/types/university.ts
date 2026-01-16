export interface University {
  asana_task_gid: string;
  university_name: string;
  researchers_count: number;
  students_count: number;
  hardware_types: string[];
  point_of_contact: string | null;
  created_at: string;
  last_synced_at: string;
}

export interface UniversityListResponse {
  universities: University[];
  total: number;
}
