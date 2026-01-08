import React, { useEffect, useState } from "react";
import DataSection from "./DataSection.tsx";
import { ItemData, FileEntry } from "../../types.ts";

// Properties passed from the Searchable Data Viewer to filter data
interface SearchBoxLoaderProperties {
  filterFunction?: (item: ItemData) => boolean;
  searchActive?: boolean;
  activeCategories: string[];
}

const SearchBoxLoader: React.FC<SearchBoxLoaderProperties> = ({
  filterFunction = () => true,
  searchActive = false,
  activeCategories
}) => {
  // Set up Arrays for use using React Hooks, This makes an array that holds data about the components on the page
  const [fileList, setFileList] = useState<FileEntry[]>([]);
  const [openSections, setOpenSections] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Fetch the file names from public using the index.json
  useEffect(() => {
    fetch("/data/index.json")
      .then((response) => {
        if (!response.ok) throw new Error(`HTTP error ${response.status}`);
        return response.json();
      })
      .then((data) => setFileList(data.files))
      .catch((error) => setError(`Failed to load index.json: ${error.message}`));
  }, []);

  // This handles the toggling of categories that show the terms or not
  const toggleSection = (fileName: string) => {
    setOpenSections((prevstates) =>
      // Checks if the prevState list includes the filename
      prevstates.includes(fileName)
        // If it does, then the list is altered to be identical except the current one
        ? prevstates.filter((file) => file !== fileName) 
        // If it does not the file is added to the list of updated states
        : [...prevstates, fileName]
    );
  };

  if (error) return <p>{error}</p>;
  if (!fileList.length) return <p>Loading data sources...</p>;

  return (
    <div role= "region" aria-label= "Search Terms Categories">
       {fileList
        .filter(({ category }) => activeCategories.includes(category))
        .map(({ file, category }) => {
          const isOpen = openSections.includes(file);
          const sectionId = `section-${file}`;

      return (
        <div key={file} className = "category-section" role = "region" 
             aria-label = {`${category}-outer-container`}>
            {/*Header Row*/}
            <div className = "category-header">
              <div className = "category-name">{category}</div>          
              <button
                id={`button-${file}`}
                role = "button"
                className={`category-toggle ${isOpen ? "open" : ""}`}
                onClick={() => toggleSection(file)}
                aria-label = {`control-visibility-${category}`}
                aria-expanded={isOpen}
                aria-controls={sectionId}
                data-label={isOpen ? "Hide" : "Show"}
              >
                <span className={isOpen ? "caret open" : "caret"}>▼</span>
              </button>
            </div>

          {/*Collapsible Content*/}
          {isOpen && (
            <div id={sectionId} className = "category-content" role="region" aria-labelledby={`terms-${category}`}>
              <DataSection fileName={file} 
                           category = {category} 
                           filterFunction = {filterFunction}
                           searchActive = {searchActive}/>
            </div>
          )}
        </div>
      );
    })}
    </div>
  );
};

export default SearchBoxLoader;
