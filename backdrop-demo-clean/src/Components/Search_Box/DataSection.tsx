import React, { useEffect, useState } from "react";
import { ItemData } from "../../types.ts";

interface DataSectionProps {
    fileName: string;
    category: string;
    filterFunction?: (item: ItemData) => boolean;
    searchActive?: boolean;
}

const DataSection: React.FC<DataSectionProps> = ({ fileName, 
                                                   category, 
                                                   filterFunction = () => true, 
                                                   searchActive = false,}) => {
    // Set up Arrays for use using React Hooks, This makes an array that holds data about the components on the page
    const [data, setData] = useState<ItemData[] | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        // Using the filename given by the loader, get the data from that file
        fetch(`/data/${fileName}`)
        .then((response) => {
            if (!response.ok) throw new Error(`HTTP error ${response.status}`);
            return response.json();
        })
        .then((json) => setData(json))
        .catch((err) => setError(`Failed to load ${fileName}: ${err.message}`));
    }, [fileName]);

    if (error) return <p>{error}</p>;
    if (!data) return <p>Loading {category}...</p>;

    // This filters and counts the data for the dropdowns
    const filteredData = data.filter(filterFunction);
    const count = searchActive ? filteredData.length : data.length;

    return (
        <div role= "region" aria-labelledby = {`heading-${category}`}>
          <div role = "list" className = "data-grid" aria-label = {`list-${category}-terms`}>
            {filteredData.length > 0 ? (
              filteredData.map((item) => (
                <div key={item.id} role="listitem" className = "data-item" aria-label = {`term-${category}-${item.name}`}>
                  <div className="item-name">{item.name}</div>
                  <div className="item-description">{item.description}</div>
                  <div className="item-cert">
                    Medical Certification Importance: {item.med_cert_importance}
                  </div>
                </div>
            ))
          ) : (
            // Still shows a message if no items match search
            <p style={{ fontStyle: "italic" }}>No matching items.</p>
          )}
          </div>
        </div>
    );
};

export default DataSection;
