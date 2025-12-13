import os
from supabase import create_client, Client
from dotenv import load_dotenv
from io import BytesIO


load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "SSIS")

def get_supabase_client() -> Client:
    """Get Supabase client instance."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_student_photo(file_data: bytes, student_id: str, file_extension: str = "jpg") -> str:
    """
    Upload a student photo to Supabase storage.
    Converts PNG to JPG for consistency, keeps JPEG as is.
    
    Args:
        file_data: Binary file data
        student_id: Student ID (used as filename)
        file_extension: File extension of uploaded file (jpg, jpeg, or png only)
    
    Returns:
        Public URL of the uploaded file
    """
    try:
        supabase = get_supabase_client()
        
        # Convert to lowercase for consistency
        file_extension = file_extension.lower()
        
        # Validate file extension (should already be validated in route, but double-check)
        if file_extension not in ['jpg', 'jpeg', 'png']:
            raise ValueError(f"Invalid file extension: {file_extension}. Only jpg, jpeg, png allowed.")
        
        # Convert PNG to JPG, keep JPEG as is
        if file_extension == 'png':
            try:
                # Open the PNG image from bytes
                image = Image.open(BytesIO(file_data))
                
                # Convert RGBA to RGB if necessary (PNG with transparency)
                if image.mode in ('RGBA', 'LA', 'P'):
                    # Create a white background for transparent PNGs
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'RGBA':
                        # Paste the image using alpha channel as mask
                        background.paste(image, mask=image.split()[3])
                    else:
                        background.paste(image)
                    image = background
                elif image.mode != 'RGB':
                    # Convert to RGB if not already
                    image = image.convert('RGB')
                
                # Convert to JPG bytes
                output = BytesIO()
                image.save(output, format='JPEG', quality=95, optimize=True)
                file_data = output.getvalue()
                file_extension = 'jpg'
                print(f"DEBUG: Converted PNG to JPG format")
                
            except Exception as conv_error:
                print(f"Error converting PNG to JPG: {str(conv_error)}")
                # If conversion fails, still force .jpg extension
                file_extension = 'jpg'
        
        # Handle jpeg -> jpg standardization
        if file_extension == 'jpeg':
            file_extension = 'jpg'
        
        # ALWAYS use .jpg extension for consistency
        filename = f"{student_id}.jpg"
        file_path = f"students/{filename}"
        
        print(f"DEBUG: Uploading file as: {filename}")
        
        # Upload file to Supabase storage
        # Use "upsert": "true" to overwrite if exists
        response = supabase.storage.from_(SUPABASE_BUCKET).upload(
            file_path,
            file_data,
            file_options={"content-type": "image/jpeg", "upsert": "true"}
        )
        
        # Get public URL
        public_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(file_path)
        
        print(f"DEBUG: Upload successful, URL: {public_url}")
        return public_url
        
    except Exception as e:
        raise Exception(f"Failed to upload photo to Supabase: {str(e)}")

def delete_student_photo(photo_url: str) -> bool:
    """
    Delete a student photo from Supabase storage.
    
    Args:
        photo_url: Public URL of the photo
    
    Returns:
        True if successful, False otherwise
    """
    try:
        if not photo_url:
            return True
        
        supabase = get_supabase_client()
        
        # Extract file path from URL
        # URL format: https://[project].supabase.co/storage/v1/object/public/[bucket]/[path]
        if "/storage/v1/object/public/" in photo_url:
            path_part = photo_url.split("/storage/v1/object/public/")[1]
            # Remove bucket name from path
            if path_part.startswith(f"{SUPABASE_BUCKET}/"):
                file_path = path_part[len(f"{SUPABASE_BUCKET}/"):]
            else:
                file_path = path_part.split("/", 1)[1] if "/" in path_part else path_part
        else:
            # Fallback: try to extract from URL
            return False
        
        # Delete file
        supabase.storage.from_(SUPABASE_BUCKET).remove([file_path])
        return True
    except Exception as e:
        print(f"Error deleting photo: {str(e)}")
        return False

