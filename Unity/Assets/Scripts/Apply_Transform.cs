using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Apply_Transform : MonoBehaviour
{
    [SerializeField] Vector3    displacement;
    [SerializeField] float      angle;
    [SerializeField] AXIS       rotationAxis;

    Mesh        mesh;
    Vector3[]   baseVertices;
    Vector3[]   newVertices;

    // Start is called before the first frame update
    void Start()
    {
        mesh = GetComponentInChildren<MeshFilter>().mesh;
        baseVertices = mesh.vertices;

        newVertices = new Vector3[baseVertices.Length];
        for (int i = 0; i < baseVertices.Length; i++)
            newVertices[i] = baseVertices[i];
        
    }

    // Update is called once per frame
    void Update()
    {
        DoTransform();
    }

    void DoTransform()
    {
        Matrix4x4 move = HW_Transforms.TranslationMat(displacement.x * Time.time, displacement.y * Time.time, displacement.z * Time.time);
        Matrix4x4 rotate = HW_Transforms.RotateMat(angle * Time.time, rotationAxis);

        Matrix4x4 posOrigin = HW_Transforms.TranslationMat(-displacement.x, -displacement.y, -displacement.z);
        Matrix4x4 posObject = HW_Transforms.TranslationMat(displacement.x, displacement.y, displacement.z);

        Matrix4x4 composite = move * rotate;

        for (int i=0; i < newVertices.Length; i++) {
            Vector4 temp = new Vector4(baseVertices[i].x, baseVertices[i].y, baseVertices[i].z, 1);
            newVertices[i] = composite * temp;
        }

        mesh.vertices = newVertices;
        mesh.RecalculateNormals();
    }
}