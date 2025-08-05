# Working with Neo4J

- Access through browser
  ```
  http://localhost:7474/
  ```

- Match Everything

  ```
  MATCH(n) RETURN n;
  ```

  - Display only Files and Commits
  ```
  MATCH(f:File)
  MATCH(c:Commit) 
  RETURN f,c;
  ```


- Delete Everything
  ```
  MATCH (n)
  DETACH DELETE n;
  ```

- Given two labels, find all they relationships they have btw them
  Example
  ```
  MATCH (d:Developer)-[r]->(c:Commit)
  RETURN DISTINCT type(r) AS RelationshipType;
  ```

- Given a label, find all relationships it has with all possible node labels
  ```
  MATCH (f:File)-[r]->(b)
  RETURN DISTINCT type(r) AS RelationshipType, labels(b) AS TargetLabels;
  ```

- Display Style
  ```
  :style 
  {
    "File": { "label": "name" },
    "Commit": { "label": "sha" }
  }
  ```