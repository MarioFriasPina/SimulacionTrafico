using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CityMaker : MonoBehaviour
{
    [SerializeField] TextAsset layout;
    [SerializeField] GameObject roadPrefab;
    [SerializeField] GameObject buildingPrefab;
    [SerializeField] GameObject semaphorePrefab;
    [SerializeField] int tileSize;

    // Start is called before the first frame update
    void Start()
    {
        MakeTiles(layout.text);
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    void MakeTiles(string tiles)
    {
        int row_size = 0;

        int x = 0;
        // Mesa has y 0 at the bottom
        // To draw from the top, find the rows of the file
        // and move down
        // Remove the last enter, and one more to start at 0
        int y = tiles.Split('\n').Length - 2;
        //Debug.Log(y);

        Vector3 position;
        GameObject tile;

        for (int i=0; i<tiles.Length; i++) {
            if (tiles[i] == '>') {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(roadPrefab, position, Quaternion.Euler(0, 270, 0));
                tile.transform.parent = transform;
                tile.name = "Road (" + x + ", " + y + ")";
                x += 1;            
            } else if (tiles[i] == '<') {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(roadPrefab, position, Quaternion.Euler(0, 90, 0));
                tile.transform.parent = transform;
                tile.name = "Road (" + x + ", " + y + ")";
                x += 1;
            } else if (tiles[i] == 'v') {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(roadPrefab, position, Quaternion.Euler(0, 0, 0));
                tile.transform.parent = transform;
                tile.name = "Road (" + x + ", " + y + ")";
                x += 1;
            } else if (tiles[i] == '^') {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(roadPrefab, position, Quaternion.Euler(0, 180, 0));
                tile.transform.parent = transform;
                tile.name = "Road (" + x + ", " + y + ")";
                x += 1;
            } else if (tiles[i] == 's' || tiles[i] == 'S') {
                Quaternion rotation = Quaternion.Euler(0, 90, 0);
                //Left
                if (tiles[i + 1] == '<')
                    rotation = Quaternion.Euler(0, 90, 0);
                //Right
                else if (tiles[i - 1] == '>')
                    rotation = Quaternion.Euler(0, 270, 0);
                //Up
                else if (tiles[i - row_size] == 'v')
                    rotation = Quaternion.Euler(0, 0, 0);
                //Down
                else if (tiles[i + row_size] == '^')
                    rotation = Quaternion.Euler(0, 180, 0);
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(roadPrefab, position, rotation);
                tile.transform.parent = transform;
                tile.name = "Road (" + x + ", " + y + ")";
                x += 1;
            } else if (tiles[i] == 'D') {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(buildingPrefab, position, Quaternion.Euler(0, 90, 0));
                tile.transform.localScale = new Vector3(0.45f, 1f, 0.45f);
                //tile.GetComponent<Renderer>().materials[0].color = Color.red;
                tile.transform.parent = transform;
                tile.name = "Destination (" + x + ", " + y + ")";
                x += 1;
            } else if (tiles[i] == '#') {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(buildingPrefab, position, Quaternion.identity);
                tile.transform.localScale = new Vector3(0.45f, Random.Range(0.1f, 0.5f), 0.45f);
                tile.transform.parent = transform;
                tile.name = "Building (" + x + ", " + y + ")";
                x += 1;
            } else if (tiles[i] == '\n') {
                row_size = x + 2;
                x = 0;
                y -= 1;
            }
        }

    }
}
