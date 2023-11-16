using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class MyLerp : MonoBehaviour
{
    [SerializeField] Vector3 initPos;
    [SerializeField] Vector3 finalPos;
    [SerializeField] float moveTime;

    float elapsedTime = 0.0f;

    float t;

    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        t = elapsedTime / moveTime;
        t = t * t * (3.0f - 2.0f * t);

        Vector3 currPos = initPos + (finalPos - initPos) * t;
        transform.position = currPos;

        elapsedTime += Time.deltaTime;

        if (elapsedTime >= moveTime) 
        {
            Vector3 temp = initPos;
            initPos = finalPos;
            finalPos = temp;

            elapsedTime = 0.0f;
        }
    }
}
