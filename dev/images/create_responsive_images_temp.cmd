@echo off
echo Generating responsive images...

magick "D:\Projects\www\GAZTank\dev\images\gaztank_favicon_RAW.png" -resize 512x512 -quality 85 "gaztank_logo_512x512.webp"
echo Created gaztank_logo_512x512.webp
magick "D:\Projects\www\GAZTank\dev\images\gaztank_favicon_RAW.png" -resize 256x256 -quality 85 "gaztank_logo_256x256.webp"
echo Created gaztank_logo_256x256.webp
magick "D:\Projects\www\GAZTank\dev\images\gaztank_favicon_RAW.png" -resize 128x128 -quality 85 "gaztank_logo_128x128.webp"
echo Created gaztank_logo_128x128.webp
magick "D:\Projects\www\GAZTank\dev\images\gaztank_favicon_RAW.png" -resize 75x75 -quality 85 "gaztank_logo_75x75.webp"
echo Created gaztank_logo_75x75.webp
magick "D:\Projects\www\GAZTank\dev\images\gaztank_favicon_RAW.png" -resize 50x50 -quality 85 "gaztank_logo_50x50.webp"
echo Created gaztank_logo_50x50.webp

magick "D:\Projects\www\GAZTank\dev\images\gaztank_favicon_RAW.png" -resize 32x32 -quality 85 "gaztank_favicon_32x32.webp"
echo Created gaztank_favicon_32x32.webp
magick "D:\Projects\www\GAZTank\dev\images\gaztank_favicon_RAW.png" -resize 16x16 -quality 85 "gaztank_favicon_16x16.webp"
echo Created gaztank_favicon_16x16.webp

echo All images generated successfully!
pause