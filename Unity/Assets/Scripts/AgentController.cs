// TC2008B. Sistemas Multiagentes y Gráficas Computacionales
// C# client to interact with Python. Based on the code provided by Sergio Ruiz.
// Octavio Navarro. October 2023

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

[Serializable]
public class AgentData
{
    /*
    The AgentData class is used to store the data of each agent.
    
    Attributes:
        id (string): The id of the agent.
        x (float): The x coordinate of the agent.
        y (float): The y coordinate of the agent.
        z (float): The z coordinate of the agent.
        state (string): The state of the agent. (Applicable only to obstacle type agents)
    */
    public string id, state;
    public float x, y, z;

    public AgentData(string id, float x, float y, float z, string state)
    {
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
        this.state = state;
    }
}

[Serializable]

public class AgentsData
{
    /*
    The AgentsData class is used to store the data of all the agents.

    Attributes:
        positions (list): A list of AgentData objects.
    */
    public List<AgentData> positions;

    public AgentsData() => this.positions = new List<AgentData>();
}

public class AgentController : MonoBehaviour
{
    /*
    The AgentController class is used to control the agents in the simulation.

    Attributes:
        serverUrl (string): The url of the server.
        getAgentsEndpoint (string): The endpoint to get the agents data.
        getObstaclesEndpoint (string): The endpoint to get the obstacles data.
        sendConfigEndpoint (string): The endpoint to send the configuration.
        updateEndpoint (string): The endpoint to update the simulation.
        agentsData (AgentsData): The data of the agents.
        obstacleData (AgentsData): The data of the obstacles.
        agents (Dictionary<string, GameObject>): A dictionary of the agents.
        prevPositions (Dictionary<string, Vector3>): A dictionary of the previous positions of the agents.
        currPositions (Dictionary<string, Vector3>): A dictionary of the current positions of the agents.
        updated (bool): A boolean to know if the simulation has been updated.
        started (bool): A boolean to know if the simulation has started.
        agentPrefab (GameObject): The prefab of the agents.
        obstaclePrefab (GameObject): The prefab of the obstacles.
        floor (GameObject): The floor of the simulation.
        NAgents (int): The number of agents.
        width (int): The width of the simulation.
        height (int): The height of the simulation.
        timeToUpdate (float): The time to update the simulation.
        timer (float): The timer to update the simulation.
        dt (float): The delta time.
    */
    string serverUrl = "http://localhost:8585";
    string getAgentsEndpoint = "/getAgents";
    string getObstaclesEndpoint = "/getObstacles";
    string sendConfigEndpoint = "/init";
    string updateEndpoint = "/update";
    AgentsData agentsData, obstacleData;
    Dictionary<string, GameObject> agents, lights;
    Dictionary<string, Vector3> prevPositions, currPositions;

    bool updated = false;

    public GameObject agentPrefab, obstaclePrefab;
    public string file;
    public float timeToUpdate = 5.0f;

    [SerializeField] int tileSize;

    private float timer, dt;

    void Start()
    {
        agentsData = new AgentsData();
        obstacleData = new AgentsData();

        prevPositions = new Dictionary<string, Vector3>();
        currPositions = new Dictionary<string, Vector3>();

        agents = new Dictionary<string, GameObject>();
        lights = new Dictionary<string, GameObject>();

        //floor.transform.localScale = new Vector3((float)width/10, 1, (float)height/10);
        //floor.transform.localPosition = new Vector3((float)width/2-0.5f, 0, (float)height/2-0.5f);
        
        timer = timeToUpdate;

        // Launches a couroutine to send the configuration to the server.
        StartCoroutine(SendConfiguration());
    }

    private void Update() 
    {
        if(timer < 0)
        {
            timer = timeToUpdate;
            updated = false;
            StartCoroutine(UpdateSimulation());
        }

        if (updated)
        {
            timer -= Time.deltaTime;
            dt = 1.0f - (timer / timeToUpdate);

            // Iterates over the agents to update their positions.
            // The positions are interpolated between the previous and current positions.
            foreach(var agent in currPositions)
            {
                Vector3 currentPosition = agent.Value;
                Vector3 previousPosition = prevPositions[agent.Key];

                Vector3 interpolated = Vector3.Lerp(previousPosition, currentPosition, dt);
                Vector3 direction = currentPosition - interpolated;

                agents[agent.Key].transform.localPosition = interpolated;
                if(direction != Vector3.zero) agents[agent.Key].transform.rotation = Quaternion.LookRotation(direction);
            }

            // float t = (timer / timeToUpdate);
            // dt = t * t * ( 3f - 2f*t);
        }
    }
 
    IEnumerator UpdateSimulation()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + updateEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            StartCoroutine(GetAgentsData());
            StartCoroutine(GetObstacleData());
        }
    }

    IEnumerator SendConfiguration()
    {
        /*
        The SendConfiguration method is used to send the configuration to the server.

        It uses a WWWForm to send the data to the server, and then it uses a UnityWebRequest to send the form.
        */
        WWWForm form = new WWWForm();

        form.AddField("file", file);

        UnityWebRequest www = UnityWebRequest.Post(serverUrl + sendConfigEndpoint, form);
        www.SetRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            Debug.Log("Configuration upload complete!");
            Debug.Log("Getting Agents positions");

            // Once the configuration has been sent, it launches a coroutine to get the agents data.
            StartCoroutine(GetAgentsData());
            StartCoroutine(GetObstacleData());
        }
    }

    IEnumerator GetAgentsData() 
    {
        // The GetAgentsData method is used to get the agents data from the server.

        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getAgentsEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            // Once the data has been received, it is stored in the agentsData variable.
            // Then, it iterates over the agentsData.positions list to update the agents positions.
            agentsData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            foreach(AgentData agent in agentsData.positions)
            {
                Vector3 newAgentPosition = new Vector3(agent.x * tileSize, agent.y, agent.z * tileSize);

                if (!agents.ContainsKey(agent.id))
                {
                    prevPositions[agent.id] = newAgentPosition;
                    agents[agent.id] = Instantiate(agentPrefab, newAgentPosition, Quaternion.identity);
                    agents[agent.id].name = agent.id;

                    Apply_transforms apply_transforms = agents[agent.id].GetComponent<Apply_transforms>(); //Get the script
                    apply_transforms.SetDestination(newAgentPosition); //Set the destination
                    //set time
                    apply_transforms.move_time = timeToUpdate;
                }
                else
                {
                    Apply_transforms apply_transforms = agents[agent.id].GetComponent<Apply_transforms>(); //Get the script
                    apply_transforms.SetDestination(newAgentPosition); //Set the destination
                }
            }
            updated = true;
        }
    }

    IEnumerator GetObstacleData() 
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getObstaclesEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            obstacleData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            //Debug.Log(obstacleData.positions);

            foreach(AgentData obstacle in obstacleData.positions)
            {
                if (!lights.ContainsKey(obstacle.id)){
                    Quaternion rotation;

                    if (obstacle.id[0] == '<') {
                        rotation = Quaternion.Euler(0, 90, 0);
                        lights[obstacle.id] = Instantiate(obstaclePrefab, new Vector3((obstacle.x - 0.5f) * tileSize, obstacle.y, (obstacle.z - 1.5f) * tileSize), rotation);
                    }
                    else if (obstacle.id[0] == '>') {
                        rotation = Quaternion.Euler(0, 270, 0);
                        lights[obstacle.id] = Instantiate(obstaclePrefab, new Vector3((obstacle.x + 0.5f) * tileSize, obstacle.y, (obstacle.z - 0.5f) * tileSize), rotation);
                    }
                    else if (obstacle.id[0] == 'v') {
                        rotation = Quaternion.Euler(0, 0, 0);
                        lights[obstacle.id] = Instantiate(obstaclePrefab, new Vector3((obstacle.x + 0.5f) * tileSize, obstacle.y, (obstacle.z - 1.5f) * tileSize), rotation);
                    }
                    else if (obstacle.id[0] == '^') {
                        rotation = Quaternion.Euler(0, 180, 0);
                        lights[obstacle.id] = Instantiate(obstaclePrefab, new Vector3((obstacle.x - 0.5f) * tileSize, obstacle.y, (obstacle.z - 0.5f) * tileSize), rotation);
                    }
                    lights[obstacle.id].name = obstacle.id;
                }
                else
                {
                    foreach(var light in lights[obstacle.id].GetComponentsInChildren<Light>(true)){
                        if (obstacle.state == "True")
                            light.color = Color.green;
                        else
                            light.color = Color.red;
                    }
                }
            }
        }
    }
}