/*
Author: Devi Granec-Boydstun
    Role: Scrum Master 2
Purpose: Represents the structure of terms in the search box component
*/

// This is the typing for the Items
export interface ItemData {
  id: number;
  name: string;
  description: string;
  med_cert_importance: string;
  category: string;
}

// This is the typing for the identification file: index.json 
export interface FileEntry {
  file: string;
  category: string;
}
