#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <unistd.h>
#include <errno.h>

char cut1[] = " - PressPlay 訂閱學習，時刻精進";

int main(){

	FILE* fp;
	char name[512];
	char *pch;
	int i,j;
	char cutstring[8][128];
	char buff[1024];
	char fullname[1024];
	memset(cutstring,'\0',sizeof(cutstring[0][0])*8*128);
	
    DIR* FD;
    struct dirent* in_file;
	char in_dir[]="/home/jerrychen/Downloads/FireShot/150_size";
   
	/* Openiing folder, to get the pdf file */
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
        if (in_file->d_type != 8)    /*if the file_type is not regular file */
            continue;

		strcpy(name,in_file->d_name);
		sprintf(buff,"%s/%s",in_dir,name);
		
		while((pch = strstr(name ,cut1))!=NULL)
		{
			*pch = '\0';
			strcat(name,".pdf");
		}
		for(i=0;i<strlen(name)-1;i++)
		{
			if(name[i] =="｜"[0] && name[i+1] =="｜"[1] && name[i+2] =="｜"[2])   /*for mutiple character(chineses), it consists of 3 ch*/
			{
				name[i]=' ';
				name[i+1]='|';
				name[i+2]=' ';
			}
		}

		i=0;
		pch=strtok(name,". ");
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

		sprintf(fullname,"%s/%s",in_dir,name);
		printf("%s\n",fullname);

		if(rename(buff,fullname)!=0)
		{
			fprintf(stderr, "Error : Failed to change file [%s] - %s\n", buff,strerror(errno));
			return -1;
		}

		memset(buff,'\0',sizeof(buff));
		memset(cutstring,'\0',sizeof(cutstring[0][0])*8*128);

    }
			
	return 0;
}
