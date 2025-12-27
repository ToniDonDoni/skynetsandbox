using UnityEngine;

public class CameraLook : MonoBehaviour
{
    public float sensitivity = 5f;

    void Start()
    {
        Input.gyro.enabled = true;
    }

    void Update()
    {
        Quaternion deviceRotation = Input.gyro.attitude;
        deviceRotation = new Quaternion(
            deviceRotation.x,
            deviceRotation.y,
            -deviceRotation.z,
            -deviceRotation.w
        );

        transform.localRotation = deviceRotation * Quaternion.Euler(90f, 0f, 0f);
    }
}
