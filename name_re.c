#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <unistd.h>
#include <errno.h>

char cut1[] = " - PressPlay 訂閱學習，時刻精進";

int main(){

	FILE* fp;
	char name[1024];
	char *pch;
	int i,j;
	char cutstring[8][128];
	char buff[1024];
	memset(cutstring,'\0',sizeof(cutstring[0][0])*8*128);
	
    DIR* FD;
    struct dirent* in_file;
	char in_dir[]="/home/jerrychen/Downloads/FireShot/150_size";
    /* Openiing common file for writing */

    if (NULL == (FD = opendir (in_dir))) 
    {
        fprintf(stderr, "Error : Failed to open input directory - %s\n", strerror(errno));
        return 1;
    }
    while ((in_file = readdir(FD))) 
    {
        if (!strcmp (in_file->d_name, "."))
            continue;
        if (!strcmp (in_file->d_name, ".."))    
            continue;

		strcpy(name,in_file->d_name);
		sprintf(buff,"%s/%s",in_dir,name);
		pch = strstr(name ,cut1);		
		*pch = '\0';	
		strcat(name,".pdf");
		for(i=0;i<strlen(name)-1;i++)
		{
			if(name[i] =="｜"[0] && name[i+1] =="｜"[1] && name[i+2] =="｜"[2])
			{
				name[i]=' ';
				name[i+1]='|';
				name[i+2]=' ';
			}
		}
		pch=strtok(name,". ");
		i=0;
		while(pch!=NULL)
		{
			strcpy(cutstring[i++],pch);
			pch=strtok(NULL," ");
		}
		sprintf(name,"%s.",cutstring[0]);
		for(j=1;j<i;j++)
		{
			strcat(name,cutstring[j]);
		}
		//printf("%s\n",name);
		char newname[1024];
		sprintf(newname,"%s/%s",in_dir,name);
		printf("%s\n",newname);

		if(rename(buff,newname)!=0)
		{
			fprintf(stderr, "Error : Failed to change file [%s] - %s\n", buff,strerror(errno));
			return -1;
		}

		memset(buff,'\0',sizeof(buff));
		memset(cutstring,'\0',sizeof(cutstring[0][0])*8*128);

    }
			
	return 0;
}
