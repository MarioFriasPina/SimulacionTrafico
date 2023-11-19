/*
    Shaul Zayat Askenazi | A01783240
*/

using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Apply_transforms : MonoBehaviour
{
    [SerializeField] Vector3 displacement;
    [SerializeField] float angle; 
    [SerializeField] AXIS rotationAXIS;

    //Wheel model
    [SerializeField] GameObject wheelModel;

    Mesh mesh;
    Vector3[] vertices;
    Vector3[] newVertices;

    [SerializeField] Wheel[] wheel;

    // Start is called before the first frame update
    void Start()
    {
        mesh = GetComponentInChildren<MeshFilter>().mesh;
        vertices = mesh.vertices;

        //Create a copy to testing the vertices
        newVertices = new Vector3 [vertices.Length];
        for (int i = 0; i<vertices.Length; i++){
            newVertices[i] = vertices[i];
        }

        //Instantiate the wheels
        for(int i = 0; i<wheel.Length; i++){
            GameObject temp = Instantiate(wheelModel, new Vector3(0,0,0), Quaternion.identity);

            //Obtain the mesh and vertices of the wheel
            wheel[i].mesh = temp.GetComponentInChildren<MeshFilter>().mesh;
            wheel[i].vertices = wheel[i].mesh.vertices;
            wheel[i].newVertices = new Vector3[wheel[i].vertices.Length];
            for(int j = 0; j<wheel[i].vertices.Length; j++){ //Create a copy of the vertices
                wheel[i].newVertices[j] = wheel[i].vertices[j];
            }
        }

    }

    //Function to obtain the new vector using displacement vectors in x and z
    //Return the angle 
    float GetAngle(Vector3 displacement){
        angle = Mathf.Atan2(displacement.x, displacement.z);
        //Transform to degrees
        angle = angle * Mathf.Rad2Deg;
        return angle;
    }


    // Update is called once per frame
    void Update()
    {
        DoTransform();
    }

    void DoTransform(){
        //Set the initial position of the wheels
        //Set the angle of the car using the displacement vector
        angle = GetAngle(displacement);
        Matrix4x4 move = HW_Transforms.TranslationMat(displacement.x *Time.time,
                                                      displacement.y *Time.time,
                                                      displacement.z *Time.time);

        Matrix4x4 rotate = HW_Transforms.RotateMat(angle, rotationAXIS);
        Matrix4x4 composite = move * rotate;

        Matrix4x4 rotate_wheel1 = HW_Transforms.RotateMat(wheel[0].rotation * Time.time, AXIS.X);
        //Print the matrix
        Debug.Log(rotate_wheel1);

        //Apply the composite for the car
        for(int i = 0; i<vertices.Length; i++){
            Vector4 temp = new Vector4(vertices[i].x,
                                       vertices[i].y,
                                       vertices[i].z,1);
            newVertices[i] = composite * temp;
        }

        //Apply the composite for all the wheels
        for(int i = 0; i<wheel.Length; i++){
            //Set the initial position of the wheels
            Matrix4x4 initial_pos_wheel = HW_Transforms.TranslationMat(wheel[i].position.x,
                                                                    wheel[i].position.y,
                                                                    wheel[i].position.z);
            //Apply the composite for each wheel
            Matrix4x4 wheel_composite = composite * initial_pos_wheel * rotate_wheel1;
            //Obtain the new vertices for each wheel
            for(int j = 0; j<wheel[i].vertices.Length; j++){
                Vector4 temp = new Vector4(wheel[i].vertices[j].x,
                                           wheel[i].vertices[j].y,
                                           wheel[i].vertices[j].z,1);
                wheel[i].newVertices[j] = wheel_composite * temp;
            }
            //Apply the new vertices to the wheels and recalculate the normals
            wheel[i].mesh.vertices = wheel[i].newVertices;
            wheel[i].mesh.RecalculateNormals();
        }

        //Apply the new vertices to the mesh and recalculate the normals
        mesh.vertices = newVertices;
        mesh.RecalculateNormals();

        
    
    }
}

//Class to store the wheels
[System.Serializable] //To show the class in the inspector
public class Wheel{

    public Mesh mesh;
    public Vector3[] vertices;
    public Vector3[] newVertices;

    [SerializeField] public Vector3 position;
    [SerializeField] public float rotation;

    public Wheel(Vector3 pos){
        position = pos;
    }
}