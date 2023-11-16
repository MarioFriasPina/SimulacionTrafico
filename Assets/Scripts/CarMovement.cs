using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CarMovement : MonoBehaviour
{
    [SerializeField] Vector3        direction;
    [SerializeField] GameObject     Car;
    [SerializeField] GameObject     Wheel;
    [SerializeField] Vector3[]      Position = new Vector3[4];
    [SerializeField] GameObject      Camera;

    Mesh        car_mesh;
    Mesh[]      wheels_mesh = new Mesh[4];
    Vector3[]   car_baseVertices;
    Vector3[]   car_newVertices;
    Vector3[][]   wheels_baseVertices = new Vector3[4][];
    Vector3[][]   wheels_newVertices = new Vector3[4][];

    Matrix4x4[]   wheel_pos = new Matrix4x4[4];
    float angle;

    // Start is called before the first frame update
    void Start()
    {
        car_mesh = Car.GetComponentInChildren<MeshFilter>().mesh;

        //Initialize car vertices
        car_baseVertices = car_mesh.vertices;
        car_newVertices = new Vector3[car_baseVertices.Length];
        for (int i = 0; i < car_baseVertices.Length; i++)
            car_newVertices[i] = car_baseVertices[i];

        for (int i = 0; i < 4; i++)
        {
            //Create wheels
            GameObject wheel_copy;
            wheel_copy = Instantiate(Wheel, new Vector3(0,0,0), Quaternion.identity);
            wheel_copy.transform.SetParent(this.transform);

            wheels_mesh[i] = wheel_copy.GetComponentInChildren<MeshFilter>().mesh;

            Vector3 pos = Position[i];
            wheel_pos[i] = HW_Transforms.TranslationMat(pos.x, pos.y, pos.z);
            wheels_baseVertices[i] = wheels_mesh[i].vertices;
            wheels_newVertices[i] = new Vector3[wheels_baseVertices[i].Length];
            for (int j = 0; j < wheels_baseVertices[i].Length; j++)
            {
                wheels_newVertices[i][j] = wheels_baseVertices[i][j];
            }
        }
    }

    // Update is called once per frame
    void Update()
    {
        angle = Mathf.Atan2(direction.z, -direction.x) * Mathf.Rad2Deg;
        DoTransform();
    }

    /// <summary>
    /// Apply the movement matrix to wheels and car
    /// </summary>
    void DoTransform()
    {
        Matrix4x4 move = HW_Transforms.TranslationMat(direction.x * Time.time, direction.y * Time.time, direction.z * Time.time);
        Matrix4x4 wheelrotate = HW_Transforms.RotateMat(120 * Time.time, AXIS.Z);
        Matrix4x4 rotate = HW_Transforms.RotateMat(angle, AXIS.Y);

        Matrix4x4 composite = move * rotate;
        
        //Apply new vertices to car
        for (int i=0; i < car_newVertices.Length; i++) {
            Vector4 temp = new Vector4(car_baseVertices[i].x, car_baseVertices[i].y, car_baseVertices[i].z, 1);
            car_newVertices[i] = composite * temp;
        }
        car_mesh.vertices = car_newVertices;
        car_mesh.RecalculateNormals();

        //Apply to wheels
        for (int i = 0; i < 4; i++)
        {
            Matrix4x4 wheelmatrix = composite * wheel_pos[i] * wheelrotate;
            for (int j = 0; j < wheels_newVertices[i].Length; j++) {
                Vector4 temp = new Vector4(wheels_baseVertices[i][j].x, wheels_baseVertices[i][j].y, wheels_baseVertices[i][j].z, 1);
                wheels_newVertices[i][j] = wheelmatrix * temp;
            }
            wheels_mesh[i].vertices = wheels_newVertices[i];
            wheels_mesh[i].RecalculateNormals();
        }
    }
}
